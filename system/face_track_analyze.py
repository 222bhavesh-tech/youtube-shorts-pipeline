r"""Face-track analysis (MediaPipe Tasks API) — crop x expression + close ranges per clip.
Outputs: output\face_track\en\<TAG>_crop_test.txt + <TAG>_track.json   (clip 01, legacy names)
         output\face_track\en\<TAG>_cropNN.txt     + <TAG>_trackNN.json (clip NN)
         <TAG> = video folder name (argv[6], default = hardcoded per video)
Usage: python face_track_analyze.py [start_sec] [dur_sec] [clipNN]
  clip 01 (legacy): python face_track_analyze.py
  clip 02:          python face_track_analyze.py 96.799 78.44 02
Seeks to start_sec, lands on the first frame with PTS >= start (the same frame
ffmpeg -ss input-seek keeps), and labels sample times t clip-relative so the
expression/enable ranges align with ffmpeg's filter clock (t=0 at clip start).
"""
import cv2, json, math, os, sys

SRC = r"D:\youtube system\output\4k video\en\I Stranded 100 People In The Wilderness For $250,000.mp4"
MODEL = r"D:\youtube system\system\assets\models\face_detector.tflite"
OUTDIR = r"D:\youtube system\output\face_track\en"
if len(sys.argv) > 4:
    SRC = sys.argv[4]          # optional: override source video
if len(sys.argv) > 5:
    OUTDIR = sys.argv[5]       # optional: override output dir (avoids NN collisions)
START = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 74.24
CLIP = sys.argv[3] if len(sys.argv) > 3 else "01"
LEGACY = (CLIP == "01" and len(sys.argv) < 6)   # legacy only w/o source/outdir override
# Shared flat folder per language (en\ / hi\): every write is prefixed with the video-folder name
# (e.g. "I Stranded 100 People_crop02.txt") so videos never collide.
TAG = "I Stranded 100 People"   # video folder name — keep in sync with SRC above
if len(sys.argv) > 6:
    TAG = sys.argv[6]           # optional: override prefix (argv[6])
CROP_FILE = TAG + ("_crop_test.txt" if LEGACY else "_crop%s.txt" % CLIP)
TRACK_FILE = TAG + ("_track.json" if LEGACY else "_track%s.json" % CLIP)
FPS = 29.97
CROP_W, CROP_H = 608, 1080
SRC_W, SRC_H = 1920, 1080

os.makedirs(OUTDIR, exist_ok=True)

import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

detector = vision.FaceDetector.create_from_options(
    vision.FaceDetectorOptions(base_options=mp_python.BaseOptions(model_asset_path=MODEL))
)

cap = cv2.VideoCapture(SRC)
if not cap.isOpened():
    sys.exit("cannot open source")

if START > 0:
    # POS_MSEC seek lands on a keyframe <= (START-3s); decode forward to the
    # first frame at/after START — same landing frame as ffmpeg's -ss input seek.
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, START - 3.0) * 1000.0)
    while cap.get(cv2.CAP_PROP_POS_MSEC) < START * 1000.0 - 0.1:
        _ok, _ = cap.read()
        if not _ok:
            sys.exit("seek overrun: cannot reach start %ss" % START)

SAMPLE_EVERY = 5  # frames -> ~6 fps
samples = []   # {t, cx, fh, close_cand, diff}
prev_small = None
frame_i = 0
end_frame = int(DUR * FPS)

mp_img_format = mp.ImageFormat.SRGB
while frame_i <= end_frame:
    ok, frame = cap.read()
    if not ok:
        break
    if frame_i % SAMPLE_EVERY == 0:
        t = frame_i / FPS
        # frame diff on small gray
        small = cv2.cvtColor(cv2.resize(frame, (480, 270)), cv2.COLOR_BGR2GRAY)
        diff = 0.0
        if prev_small is not None:
            diff = float(cv2.absdiff(small, prev_small).mean())
        prev_small = small

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = mp.Image(image_format=mp_img_format, data=rgb)
        res = detector.detect(img)
        cx, fh = None, 0.0
        if res.detections:
            best = None
            for d in res.detections:
                bb = d.bounding_box
                area = bb.width * bb.height
                if best is None or area > best[0]:
                    best = (area, bb)
            bb = best[1]
            cx = bb.origin_x + bb.width / 2.0
            fh = float(bb.height)
        samples.append({"t": round(t, 3), "cx": cx, "fh": round(fh, 1), "diff": round(diff, 1)})
    frame_i += 1
cap.release()
detector.close()

n = len(samples)
if n < 10:
    sys.exit(f"too few samples: {n}")
print(f"samples: {n}  span: {samples[0]['t']}s -> {samples[-1]['t']}s")

# ---- close/wide classification with hysteresis ----
ENTER = 0.15 * SRC_H   # ~162px face height to enter close
EXIT = 0.10 * SRC_H    # ~108px to leave close
MIN_DUR = 0.6          # seconds
CONSSEC = 3            # consecutive samples to flip

state = False          # start wide until proven close
cand = None
cand_count = 0
raw = []
for s in samples:
    if s["fh"] >= ENTER:
        c = True
    elif s["fh"] <= EXIT or s["cx"] is None:
        c = False
    else:
        c = state  # in-between: hold
    if c == state:
        cand = None; cand_count = 0
    else:
        if c == cand:
            cand_count += 1
            if cand_count >= CONSSEC:
                state = c
                cand = None; cand_count = 0
        else:
            cand = c; cand_count = 1
    raw.append(state)

# ---- merge segments shorter than MIN_DUR into previous ----
def segs(flags):
    out = []
    st = 0
    for i in range(1, len(flags) + 1):
        if i == len(flags) or flags[i] != flags[st]:
            out.append([st, i, flags[st]])
            st = i
    return out

seg = segs(raw)
changed = True
while changed and len(seg) > 1:
    changed = False
    for i, (a, b, v) in enumerate(seg):
        dur = samples[b - 1]["t"] - samples[a]["t"]
        if dur < MIN_DUR and not (i == 0 and v is False):
            # flip this segment to previous state
            prev_v = seg[i - 1][2] if i > 0 else (seg[i + 1][2] if len(seg) > 1 else False)
            seg[i] = [a, b, prev_v]
            # relabel raw
            for j in range(a, b):
                raw[j] = prev_v
            # merge with neighbors of same value
            merged = [seg[0]]
            for sgm in seg[1:]:
                if sgm[2] == merged[-1][2]:
                    merged[-1] = [merged[-1][0], sgm[1], sgm[2]]
                else:
                    merged.append(sgm)
            seg = merged
            changed = True
            break

# ---- scene-cut snapping (within +-0.4s, not at 0/DUR) ----
cuts = [s["t"] for s in samples if s["diff"] > 35]
bounds = sorted({samples[b - 1]["t"] for a, b, v in seg if b < n})
new_bounds = []
for b in bounds:
    near = [c for c in cuts if abs(c - b) <= 0.4 and 0.5 < c < DUR - 0.5]
    new_bounds.append(min(near, key=lambda c: abs(c - b)) if near else b)
# rebuild segs with snapped bounds (reclassify raw by time)
final_ranges = []
prev_t = 0.0
bound_set = sorted(set(new_bounds))
pts = [0.0] + bound_set + [DUR]
# flag each new interval by the RAW flag at its midpoint (robust to snapping)
import bisect
_ts = [x["t"] for x in samples]
flags_pts = []
for i in range(len(pts) - 1):
    m = (pts[i] + pts[i + 1]) / 2
    j = min(bisect.bisect_left(_ts, m), len(raw) - 1)
    flags_pts.append(raw[j])
close_ranges = []
for i in range(len(pts) - 1):
    if flags_pts[i]:
        close_ranges.append([round(pts[i], 3), round(pts[i + 1], 3)])
# merge adjacent
merged = []
for r in close_ranges:
    if merged and abs(merged[-1][1] - r[0]) < 0.05:
        merged[-1][1] = r[1]
    else:
        merged.append(r)
close_ranges = merged

# ---- crop x series ----
last_x = (SRC_W - CROP_W) / 2
xs = []
for s in samples:
    if s["cx"] is not None:
        x = s["cx"] - CROP_W / 2
        x = max(0.0, min(SRC_W - CROP_W, x))
        last_x = x
    xs.append(last_x)

# EMA smooth
ALPHA = 0.35
sm = [xs[0]]
for v in xs[1:]:
    sm.append(ALPHA * v + (1 - ALPHA) * sm[-1])

# decimate: keep if moved >=10px or >=2.0s since last kept
KEEP_T = [(samples[0]["t"], sm[0])]
for i in range(1, n - 1):
    lt, lv = KEEP_T[-1]
    if abs(sm[i] - lv) >= 10 or (samples[i]["t"] - lt) >= 2.0:
        KEEP_T.append((samples[i]["t"], sm[i]))
KEEP_T.append((samples[-1]["t"], sm[-1]))

# piecewise-linear expression as a BALANCED if-tree.
# ffmpeg 9.0.1 rejects expressions nested deeper than 98 (99 fails, error:
# "Failed to configure input pad on Parsed_crop"). A right-leaning if() chain
# over N control points has depth ~N*4, which blows the limit for long clips
# (167 points -> ~670). A balanced binary split over the time axis routes t to
# the segment containing it with depth ~log2(N), staying far under the cap.
def fmt(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s else "0"

M = len(KEEP_T)

def seg(k):
    t0, x0 = KEEP_T[k]
    t1, x1 = KEEP_T[k + 1]
    dt = (t1 - t0) or 1.0
    return f"({fmt(x0)})+(({fmt(x1)})-({fmt(x0)}))*(t-({fmt(t0)}))/({fmt(dt)})"

def build(lo, hi):
    """if-tree over anchors[lo..hi] (hi-lo>=1). Caller guarantees t in [t_lo,t_hi]."""
    if hi - lo == 1:
        return seg(lo)
    m = (lo + hi) // 2
    tm = fmt(KEEP_T[m][0])
    return f"if(lt(t,{tm}),{build(lo, m)},{build(m, hi)})"

if M <= 1:
    expr = fmt(KEEP_T[0][1])
else:
    expr = (
        f"if(lt(t,{fmt(KEEP_T[0][0])}),{fmt(KEEP_T[0][1])},"
        f"if(lt(t,{fmt(KEEP_T[-1][0])}),{build(0, M - 1)},{fmt(KEEP_T[-1][1])}))"
    )

def expr_nesting(s):
    d = mx = 0
    for ch in s:
        if ch == "(":
            d += 1
            mx = max(mx, d)
        elif ch == ")":
            d -= 1
    return mx

_nest = expr_nesting(expr)
if _nest > 120:
    sys.exit(f"expression nesting {_nest} exceeds safe budget (ffmpeg cap=98 depth)")

enable = "+".join(f"between(t,{fmt(a)},{fmt(b)})" for a, b in close_ranges) or "0"

with open(os.path.join(OUTDIR, CROP_FILE), "w") as f:
    f.write(expr)

close_dur = sum(b - a for a, b in close_ranges)
info = {
    "clip": CLIP, "start": START, "dur": DUR,
    "crop": [CROP_W, CROP_H],
    "n_samples": n,
    "n_control_points": M,
    "expr_len": len(expr),
    "expr_nesting": _nest,
    "close_ranges": close_ranges,
    "enable_expr": enable,
    "close_seconds": round(close_dur, 2),
    "wide_seconds": round(DUR - close_dur, 2),
    "scene_cuts": [round(c, 2) for c in cuts],
    "samples": samples,
}
with open(os.path.join(OUTDIR, TRACK_FILE), "w") as f:
    json.dump(info, f, indent=2)

print(json.dumps({k: v for k, v in info.items() if k != "enable_expr"}, indent=2))
print("enable:", enable[:300])
