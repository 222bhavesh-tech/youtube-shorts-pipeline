# Stage 4 encode — ONE ffmpeg pass per clip (canonical Mode B dual A+B graph),
# h264_nvenc, max 2 concurrent (Quadro P620 2GB), cwd = output\temp.
# Usage: python encode_stage4.py [NN ...]   (default: all 15)
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

PROJ = r"D:\youtube system"
TEMP = os.path.join(PROJ, "output", "temp")
import src_profile
PROF, ARGS = src_profile.load(sys.argv[1:])
SRC  = PROF["src"]
FDIR = PROF["fdir"]
TAG  = PROF["tag"]
BASE = PROF["base"]
MOMENTS = PROF["moments"]
FFMPEG = (r"C:\Users\bhavesh jeengar\AppData\Local\Microsoft\WinGet\Packages"
          r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe")
PILL = os.path.join(PROJ, "system", "assets", "hook_pill.png")
LCS  = os.path.join(PROJ, "system", "assets", "overlays", "like-comment-subscribe.mp4")
CS   = os.path.join(PROJ, "system", "assets", "overlays", "center-subscribe.mov")
# REMOVED permanently (user 2026-09-26): notification-bell + youtube-subscribe
# froze in place to clip end instead of exiting smoothly — never re-add.

SLUGS = {
 1: "bought-the-grocery-store", 2: "electronics-aisle",     3: "produce-goes-bad-fast",
 4: "building-a-wall",          5: "never-thought-id-see",  6: "scanning-another-10k",
 7: "days-blended-together",    8: "race-car-track",        9: "sixty-thousand-ready",
10: "three-hundred-sixty-k",   11: "hanging-out-again",    12: "its-freezing",
13: "busted-the-pool",         14: "are-you-there-jimmy",  15: "sea-of-money",
}
SLUGS = PROF.get("slugs") or SLUGS   # profile-authored slugs override legacy

# Two-pass measured linear loudnorm for clips where single-pass missed the
# -14 +/-0.6 LU QC (measured on source segment; analysis-only pass).
# Measurements are PER SOURCE — a profile must carry its own ("measured":
# {} = none measured yet); the legacy dict below only ever applies to
# grocery (no-profile runs). Applied AFTER this block so profiles win.
MEASURED = {
 # 13: source 940.439->+78.845 ; real I -15.53 TP -2.46 LRA 13.10 TH -26.71.
 # loudnorm init() only enters LINEAR_MODE if (measured_TP + gain <= target_TP)
 # AND (measured_LRA <= target_LRA): real values fail BOTH (-0.93 > -1,
 # 13.10 > 11) -> dynamic fallback outputs -15.4 (fails QC). Present the
 # TP-capped effective values: gain +1.45 => TP -1.01 <= -1, I ~= -14.08.
 # measured_LRA only gates the mode decision (linear applies pure constant
 # gain; it never uses LRA) -> set at target so linear engages.
 13: {"I": "-15.45", "TP": "-2.46", "LRA": "11.00", "TH": "-26.71"},
 # 15: source 1100.432->+81.329 ; passes both conditions as measured
 # (offset_tp -1.26 <= -1, LRA 7 <= 11) -> linear already engaged (QC -14.0).
 15: {"I": "-13.60", "TP": "-0.86", "LRA": "7.00",  "TH": "-24.14"},
}
MEASURED = PROF["measured"] if "measured" in PROF else MEASURED

def loudnorm_chain(nn_int):
    m = MEASURED.get(nn_int)
    if m:
        return (f"loudnorm=I=-14:TP=-1:LRA=11"
                f":measured_I={m['I']}:measured_TP={m['TP']}"
                f":measured_LRA={m['LRA']}:measured_thresh={m['TH']}:linear=true")
    return "loudnorm=I=-14:TP=-1:LRA=11"

def build_fc(nn, dur, nn_int):
    expr = open(os.path.join(FDIR, f"{TAG}_crop{nn}.txt"), encoding="utf-8").read().strip()
    track = json.load(open(os.path.join(FDIR, f"{TAG}_track{nn}.json"), encoding="utf-8"))
    close = track.get("enable_expr") or "0"
    vfade = round(dur - 1.5, 3)
    afade = round(dur - 1.0, 3)
    # 70s stacked Top Overlay Timeline (rules.md):
    #   hook  1-15s  fade in 0.5 @1 + fade out 0.5 @14.5, drawtext baked on
    #         the (looped) pill canvas so text fades with the pill
    #   LCS   25->30s — FULL 5s asset plays (LIKE->COMMENT->SUBSCRIBE cycle
    #         + built-in collapse-outro that ends empty) -> auto-removed
    #         when the overlay video finishes. USER 2026-09-27: NO frozen
    #         hold — the old trim@4.0+tpad froze SUBSCRIBE in place to clip
    #         end instead of letting it exit; never re-add the freeze
    #         (bell + YS stay removed too). After EOF the empty last frame
    #         repeats -> invisible.
    #     LCS  x=268 y=56 (USER 2026-09-28 corrected) -> 544x107 content
    #          centered at (540,192), the middle of the 384px top zone.
    #          Was y=179 (bottom-center, visible y 262..368). x=268
    #          stays: 127/826 was the OLD CS coordinate (CS is now
    #          991-wide at x=44.5) and would drag the 544px LCS
    #          141px left of center.
    #   hook stays x=0 y=84 (alone 1-15s, fades).
    # CS (center-subscribe) 60->69.4 — USER 2026-09-28 CORRECTED spec:
    #   bounce pop-in 60->60.3 (scale 0->1 over 0.3s), hold, bounce-out
    #   69->69.3, then empty until the global end fade — replaces the
    #   old gte(t,60) hold-to-end. enable closes at 69.4: src runs
    #   30000/1001 while CS is 30fps, so the clocks drift ~70ms by t=69;
    #   69.4 lets the ramp reach 0 under either overlay pairing model
    #   (worst case a 2px clamp dot for 3 frames, invisible).
    #   Geometry MEASURED on f296 (the frame loop holds = the only one
    #   on-screen in the window): content 512x143, content-center offset
    #   (414.8, 234) in the 826x464 canvas -> ratios (0.5022, 0.5043).
    #   USER 2026-09-29: overlay size +20% -> 991x558 canvas (content
    #   614x172, center offset (497.7, 281.4)) -> x=44.5 y=534.6 pins
    #   that center to the MAIN band center (540,816) at full size.
    #   (The relayed y=691 assumed a 250px-tall asset; real content is
    #   143px — 691 would sit 109px below zone center.)
    #   Bounce mechanics — three traps, each TESTED on the WinGet 7.1.1
    #   build: (1) scale defaults to eval=init and REJECTS t-exprs
    #   ("not valid in init eval_mode") -> eval=frame mandatory;
    #   (2) w=0 does NOT mean empty — scale reads 0 as "input width"
    #   (would flash the full 4K canvas) -> clamp w>=2;
    #   (3) setpts+60 is GONE — loop= keeps pts on the clip timeline so
    #   scale's t and enable's t share one clock (overlay pairs inputs
    #   BY PTS, test-verified); setpts would push scale's t domain past
    #   60 before the loop even starts.
    #   overlay x/y carry the same K so the shrinking canvas re-anchors
    #   and the pop scales about the content center, not its top-left.
    #   Two-stage scale: static 4K->991 runs once per input frame (300
    #   frames), the K-scale runs on loop output (991-wide) — same cost
    #   class as before.
    #   Asset tail is EMPTY: last visible frame = f296 (t=9.87), f297-299
    #   transparent -> loop=loop=-1:size=1:start=296 drops the empty tail
    #   and clone-holds f296 (bisect-verified 2026-09-27; the older tpad
    #   clone held the EMPTY frame -> "cut before video end"; trim/select
    #   6x slower; bare/no-hold dies ~69.9 — never re-add).
    # Input order: [0]=src [1]=PILL(-framerate 30 -loop 1 -t DUR) [2]=LCS
    #              [3]=CS. CS loop-hold is infinite ->
    #   the output -t DUR in encode() bounds the graph to clip length.
    # Bounce factor K (0->1->0 over 60..69.3): drives scale w AND the
    # x/y re-anchor; min/max only because the eval lib has no clip().
    K = "min(min(max((t-60)/0.3,0),1),1-min(max((t-69)/0.3,0),1))"
    return f"""[1:v]format=rgba,drawtext=fontfile='fonts/montserrat-bold.ttf':textfile='hook{nn}.txt':fontsize=40:fontcolor=black:x='(W-text_w)/2':y='(H-text_h)/2',fade=t=in:st=1:d=0.5:alpha=1,fade=t=out:st=14.5:d=0.5:alpha=1[hook];
[0:v]split=3[fa0][fb0][fg0];
[fa0]crop=608:1080:x='{expr}':y=0,scale=1080:1920:flags=lanczos[fa];
[fb0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.25[fb];
[fg0]scale=1080:864:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:864[fg];
[fb][fg]overlay=0:384[wide];
[wide][fa]overlay=0:0:enable='{close}'[vbase];
[vbase]ass='{nn}.ass':fontsdir='fonts'[sub];
[sub][hook]overlay=0:84:enable='between(t,1,15)'[t1];
[2:v]format=rgba,setpts=PTS+25/TB[lcs];
[t1][lcs]overlay=x=268:y=56:enable='gte(t,25)'[t2];
[3:v]format=rgba,scale=991:-2,loop=loop=-1:size=1:start=296,scale=w='max(2,991*{K})':h=-2:eval=frame[cs];
[t2][cs]overlay=x='44.5+495.5*(1-{K})':y='534.6+279*(1-{K})':enable='between(t,60,69.4)'[t3];
[t3]fade=t=in:st=0:d=0.5,fade=t=out:st={vfade}:d=1.5,fps=30000/1001,format=yuv420p[vout];
[0:a]{{ln}},afade=t=in:st=0:d=0.5,afade=t=out:st={afade}:d=1[aout]""".replace("{ln}", loudnorm_chain(nn_int))

def encode(m):
    nn = f"{m['nn']:02d}"
    out = os.path.join(BASE, "clips", f"{nn}_{SLUGS[m['nn']]}.mp4")
    okm = os.path.join(TEMP, f"enc{nn}.ok")
    # marker is per-CLIP number, encodes are per-SOURCE: trust it only when
    # its owner TAG matches this profile (else re-encoding mansion after
    # bunker ran would false-skip on bunker's marker+the old output).
    owner = ""
    if os.path.exists(okm):
        try:
            owner = open(okm, encoding="utf-8").read().strip()
        except OSError:
            owner = ""
    if owner == TAG and os.path.exists(out) and os.path.getsize(out) > 20_000_000:
        return f"{nn} SKIP already-done"
    fc = build_fc(nn, m["dur"], m["nn"])
    args = [FFMPEG, "-y", "-ss", str(m["start"]), "-t", str(m["dur"]), "-i", SRC,
            # pill needs real timestamps for fade=in:st=1/out:st=14.5 — a
            # single-frame image carries pts=0 and would freeze at alpha 0
            "-framerate", "30", "-loop", "1", "-t", str(m["dur"]), "-i", PILL,
            "-i", LCS, "-i", CS,
            "-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
            "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18",
            "-b:v", "0", "-spatial-aq", "1",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            # output limit: the CS loop-hold makes that secondary infinite —
            # this bounds the graph to exactly clip length
            "-t", str(m["dur"]), out]
    env = dict(os.environ)
    env.pop("CUDA_VISIBLE_DEVICES", None)   # NVENC silently fails with -1
    t0 = time.time()
    r = subprocess.run(args, cwd=TEMP, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    with open(os.path.join(TEMP, f"enc{nn}.log"), "w", encoding="utf-8") as f:
        f.write(f"rc={r.returncode}\n=== STDERR (tail) ===\n" + (r.stderr or "")[-24000:])
    dt = time.time() - t0
    if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 1_000_000:
        with open(okm, "w", encoding="utf-8") as f: f.write(TAG)
        return f"{nn} OK {dt:.0f}s {os.path.getsize(out)//1048576}MB -> {os.path.basename(out)}"
    return f"{nn} FAIL rc={r.returncode} {dt:.0f}s (enc{nn}.log)"

def main():
    moments = json.load(open(MOMENTS, encoding="utf-8"))
    if ARGS:
        sel = set(ARGS)
        moments = [m for m in moments if f"{m['nn']:02d}" in sel]
    os.makedirs(os.path.join(BASE, "clips"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "metadata"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "ass"), exist_ok=True)
    print(f"encode: {len(moments)} clips, workers=2, cwd={TEMP}", flush=True)
    fails = 0
    with ThreadPoolExecutor(max_workers=2) as ex:
        for r in ex.map(encode, moments):
            if "FAIL" in r: fails += 1
            print(r, flush=True)
    print(f"encode done, fails={fails}", flush=True)
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
