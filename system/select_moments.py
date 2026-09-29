# Stage 3 v4: 15 non-overlapping clips — 70s FIXED target, sentence-snap window
# 65-75s (tolerance band around 70 so a sentence always lands in the window).
# The old "consume the source tail on the last clip" force is gone — it would
# have produced a >75s final clip, violating the 70s-fixed rule.
# START = sentence-start cue that makes a decent hook (skip short/dup cues, gap<=4s).
# END = sentence-start cue (or scene cut <=0.6s before it) -> no mid-sentence cuts.
import re, json, sys

# argv: [1]=scene_txt [2]=plain_txt [3]=out_json [4]=video_end [5]=n
# defaults = legacy tnTP (grocery) source; e.g. production run:
#   python select_moments.py scene_mansion.txt plain_mansion.txt moments_mansion.json 3470.896 15
VIDEO_END = float(sys.argv[4]) if len(sys.argv) > 4 else 1181.761
N = int(sys.argv[5]) if len(sys.argv) > 5 else 15
SCENE = sys.argv[1] if len(sys.argv) > 1 else r"D:\youtube system\output\temp\scene_tnTP.txt"
PLAIN = sys.argv[2] if len(sys.argv) > 2 else r"D:\youtube system\output\transcript\en\plain.txt"
OUT_JSON = sys.argv[3] if len(sys.argv) > 3 else r"D:\youtube system\output\temp\moments_tnTP.json"

# --- scene cuts ---
# PS `2>` redirection writes UTF-16LE (BOM ff fe); accept both encodings.
cuts = []
pat = re.compile(r"pts_time:\s*([0-9]+(?:\.[0-9]+)?)")
raw = open(SCENE, "rb").read()
txt = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") \
      else raw.decode("utf-8", errors="ignore")
for line in txt.splitlines():
    if "pts_time" in line:
        m = pat.search(line)
        if m:
            cuts.append(float(m.group(1)))
cuts = sorted(set(cuts))

# --- cues ---
cues = []
with open(PLAIN, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line.startswith("["):
            continue
        ts = line[1:line.index("]")]
        text = line[line.index("]") + 1:].strip()
        h, m, s = ts.split(":")
        t = int(h) * 3600 + int(m) * 60 + float(s.replace(",", "."))
        cues.append([round(t, 3), text])

# sentence starts as (time, cue_idx); t=0 always a start
sent = [(0.0, 0)]
for i in range(1, len(cues)):
    if cues[i - 1][1].endswith((".", "!", "?")):
        sent.append((cues[i][0], i))

WEAK_EXACT = {"okay.", "yeah.", "nice.", "no.", "really?", "yes."}

def hook_ok(idx):
    txt = cues[idx][1]
    if len(txt) < 12:
        return False
    if txt.lower() in WEAK_EXACT:
        return False
    if idx > 0 and cues[idx - 1][1] == txt:   # repeated caption line
        return False
    return True

def pick_start(min_t):
    """first sentence start >= min_t with a decent hook within 4s, else the first one"""
    cands = [s for s in sent if s[0] >= min_t - 0.001]
    if not cands:
        return None
    for t, idx in cands:
        if t - min_t > 4.0:
            break
        if hook_ok(idx):
            return round(t, 3)
    return round(cands[0][0], 3)

def snap_back_cut(cue_t, lo):
    best = None
    for c in cuts:
        if max(lo, cue_t - 0.6) <= c < cue_t:
            best = c if best is None or c > best else best
    return round(best, 3) if best else None

clips = []
start = 0.0
for i in range(N):
    left = N - i
    is_last = left == 1
    # True minimum reserve: each remaining clip only NEEDS 65s (validation
    # floor) + 1.5s gap slack, not a flat 70. On tight sources (bunker
    # 1037s: 15x65 + gaps fits, 15x70 does not) the old 70/clip reserve
    # capped clip 1 at 55s < lo 65 -> immediate break, 0 clips. For any
    # source where 15x70 fits comfortably the cap stays >= start+75, so
    # hi = min(cap, start+75) behaves EXACTLY as before (long sources
    # unchanged: mansion/stranded/extreme/underground all hit start+75).
    cap = VIDEO_END if is_last else VIDEO_END - (left - 1) * 65.0 - 2.0
    # Sentence-snap window [start+65, start+75]. A speech gap wider than
    # the 10s band can leave it EMPTY (stranded clip 09: next sentence
    # start 620.64 missed hi=620.28 by 0.36s -> old code broke, 8/15).
    # Step the start to the next sentence start and retry — never widen
    # the band (65-75 is the 70s-fixed contract) and never end on a scene
    # cut inside active speech (mid-sentence caption/audio cut).
    # Sources without an empty window never enter this loop -> output
    # byte-identical to the validated bunker/bn0/mansion runs.
    adv = 0
    while True:
        lo = start + 65.0
        hi = min(cap, start + 75.0)
        if hi < lo:
            start = None
            break
        avail = (VIDEO_END - 2.0 - start - 1.5 * (left - 1)) / left
        if avail < 65.0:
            start = None
            break
        target = start + min(70.0, avail)   # sentence closest to target
        times = [t for t, _ in sent if lo - 0.001 <= t <= hi]
        if times:
            break
        adv += 1
        nxt = pick_start(start + 0.01)      # strictly the NEXT sentence start
        if adv > 16 or nxt is None or nxt <= start:
            start = None
            break
        start = nxt
    if start is None:
        break
    under = [t for t in times if t <= target]
    cue_end = max(under) if under else min(times)
    end = snap_back_cut(cue_end, lo)
    end = end if (end is not None and end >= lo) else round(cue_end, 3)
    dur = round(end - start, 3)
    if dur < 65.0:
        break
    clips.append({"nn": i + 1, "start": round(start, 3), "end": end, "dur": dur})
    nxt = pick_start(end)
    if nxt is None:
        break
    start = nxt

# ---- validate ----
ok = len(clips) == N
prev = -1.0
for c in clips:
    # 64.99: times filter allows t = lo-0.001, so accept that hair of slop
    if not (64.99 <= c["dur"] <= 75.0) or c["start"] < prev:
        ok = False
        print("FAIL", c)
    prev = c["end"]

print(f"cuts={len(cuts)} cues={len(cues)} sent={len(sent)} "
      f"clips={len(clips)} valid={ok}")
for c in clips:
    sh, sm = divmod(c["start"], 3600); sm, ss = divmod(sm, 60)
    eh, em = divmod(c["end"], 3600); em, es = divmod(em, 60)
    print(f"{c['nn']:02d}  {int(sh):02d}:{int(sm):02d}:{ss:06.3f} -> "
          f"{int(eh):02d}:{int(em):02d}:{es:06.3f}  dur={c['dur']:.3f}")

if ok:
    with open(OUT_JSON, "w") as f:
        json.dump(clips, f, indent=1)
    print("saved", OUT_JSON)
