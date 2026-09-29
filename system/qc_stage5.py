# Stage 5 QC — per prompt.md: 65-120s (target 70s; wide window so the legacy
# 75-120s videos still pass), 1080x1920, h264, aac, avg_frame_rate
# exactly 30000/1001, 2 streams, size < 2GB, last-frame YAVG 14.5-22,
# integrated loudness within 0.6 LU of -14.
# Usage: python qc_stage5.py [NN ...]   (default: all 15)
import json, os, re, subprocess, sys

PROJ = r"D:\youtube system"
TEMP = os.path.join(PROJ, "output", "temp")
import src_profile
PROF, ARGS = src_profile.load(sys.argv[1:])
BASE = PROF["base"]
CLIPS = os.path.join(BASE, "clips")
MOMENTS = PROF["moments"]

SLUGS = {
 1: "bought-the-grocery-store", 2: "electronics-aisle",     3: "produce-goes-bad-fast",
 4: "building-a-wall",          5: "never-thought-id-see",  6: "scanning-another-10k",
 7: "days-blended-together",    8: "race-car-track",        9: "sixty-thousand-ready",
10: "three-hundred-sixty-k",   11: "hanging-out-again",    12: "its-freezing",
13: "busted-the-pool",         14: "are-you-there-jimmy",  15: "sea-of-money",
}
SLUGS = PROF.get("slugs") or SLUGS   # profile-authored slugs override legacy

def run(args):
    return subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")

def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
             "-print_format", "json", path])
    return json.loads(r.stdout)

def last_yavg(path):
    """YAVG series of the final 0.3s (full-decode window via -sseof)."""
    r = run(["ffmpeg", "-hide_banner", "-sseof", "-0.3", "-i", path,
             "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG",
             "-f", "null", "-"])
    vals = [float(m) for m in re.findall(r"YAVG=([0-9.]+)", r.stderr or "")]
    return vals

def integrated_lufs(path):
    r = run(["ffmpeg", "-hide_banner", "-i", path, "-map", "0:a",
             "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = (r.stderr or "")
    idx = tail.rfind("Summary:")
    seg = tail[idx:] if idx >= 0 else tail
    m = re.search(r"I:\s*(-?inf|-?\d+(?:\.\d+)?)\s*LUFS", seg)
    return float(m.group(1)) if m and m.group(1) != "-inf" else None

def qc(nn):
    slug = SLUGS[int(nn)]
    path = os.path.join(CLIPS, f"{nn}_{slug}.mp4")
    fails = []
    if not os.path.exists(path):
        return nn, [f"missing file {os.path.basename(path)}"], {}
    info = probe(path)
    vs = [s for s in info["streams"] if s["codec_type"] == "video"]
    aus = [s for s in info["streams"] if s["codec_type"] == "audio"]
    stats = {}
    if len(info["streams"]) != 2:
        fails.append(f"streams={len(info['streams'])} (want 2)")
    if len(vs) != 1:
        fails.append(f"video streams={len(vs)}")
    else:
        v = vs[0]
        stats["v"] = f"{v['codec_name']} {v['width']}x{v['height']} {v['pix_fmt']} @{v['avg_frame_rate']}"
        if v["codec_name"] != "h264": fails.append(f"codec={v['codec_name']}")
        if (v["width"], v["height"]) != (1080, 1920):
            fails.append(f"dims={v['width']}x{v['height']}")
        if v["pix_fmt"] != "yuv420p": fails.append(f"pix_fmt={v['pix_fmt']}")
        if v["avg_frame_rate"] != "30000/1001":
            fails.append(f"fps={v['avg_frame_rate']}")
    if len(aus) != 1:
        fails.append(f"audio streams={len(aus)}")
    else:
        a = aus[0]
        stats["a"] = f"{a['codec_name']} {a['sample_rate']}Hz"
        if a["codec_name"] != "aac": fails.append(f"acodec={a['codec_name']}")
        if a["sample_rate"] != "48000": fails.append(f"rate={a['sample_rate']}")
    dur = float(info["format"]["duration"])
    size = int(info["format"]["size"])
    stats["dur"] = round(dur, 3); stats["size_mb"] = size // 1048576
    if not (65.0 <= dur <= 120.0): fails.append(f"dur={dur}")
    if size >= 2 * 1024**3: fails.append(f"size={size}")
    y = last_yavg(path)
    stats["yavg_last"] = round(y[-1], 1) if y else None
    stats["yavg_win"] = [round(v, 1) for v in y] if y else []
    if not y:
        fails.append("YAVG no frames")
    else:
        if not (14.5 <= y[-1] <= 22.0):
            fails.append(f"YAVG_last={y[-1]:.1f}")
        # fade must converge to limited-range black (Y=16: vf_fade interpolates
        # toward black_level=16). Content brighter than 16 declines toward 16,
        # content darker than 16 rises toward 16 — both are correct fades.
        if abs(y[-1] - 16) > abs(y[0] - 16):
            fails.append("YAVG not converging to black")
        if any(y[i + 1] - y[i] > 3.0 for i in range(len(y) - 1)):
            fails.append("YAVG rising inside fade-out")
    lufs = integrated_lufs(path)
    stats["lufs"] = round(lufs, 2) if lufs is not None else None
    if lufs is None:
        fails.append("loudness unmeasurable")
    elif abs(lufs - (-14.0)) > 0.6:
        fails.append(f"LUFS={lufs:.2f} (tol 0.6)")
    return nn, fails, stats

def main():
    moments = json.load(open(MOMENTS, encoding="utf-8"))
    allnn = [f"{m['nn']:02d}" for m in moments]
    sel = [f"{n:02d}" if str(n).isdigit() and len(str(n)) == 1 else str(n) for n in ARGS] or allnn
    total_fail = 0
    for nn in sel:
        nn, fails, st = qc(nn)
        tag = "PASS" if not fails else "FAIL"
        if fails: total_fail += 1
        line = (f"{nn} {tag} dur={st.get('dur')}s {st.get('size_mb')}MB "
                f"YAVG={st.get('yavg_last')} LUFS={st.get('lufs')} | {st.get('v','')} | {st.get('a','')}")
        print(line, flush=True)
        if fails:
            for f in fails: print(f"     - {f}", flush=True)
    print(f"QC: {len(sel)} checked, {total_fail} failed", flush=True)
    sys.exit(1 if total_fail else 0)

if __name__ == "__main__":
    main()
