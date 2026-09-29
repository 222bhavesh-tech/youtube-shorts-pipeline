# Stage 3 helper: dump per-clip plain-text content for authoring hooks/slugs/meta.
# Usage: python clip_dump.py profile.json            (all clips)
#        python clip_dump.py profile.json 03 07      (selected clips)
#        python clip_dump.py moments.json plain.txt  (pre-profile authoring)
# Reads profile->moments + profile->plain; prints sentences inside each window.
import io, json, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def _peek(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


if len(sys.argv) > 1:
    a1 = sys.argv[1]
    # moments_*.json is a LIST; profile *.json is an OBJECT -> route by shape
    if a1.lower().endswith(".json") and isinstance(_peek(a1), dict):
        import src_profile
        PROF, ARGS = src_profile.load(sys.argv[1:])
        MOMENTS, PLAIN, SEL = PROF["moments"], PROF["plain"], set(ARGS)
    else:
        MOMENTS, PLAIN, SEL = a1, sys.argv[2], set(sys.argv[3:])
else:
    raise SystemExit("usage: clip_dump.py profile.json [NN...] | moments.json plain.txt [NN...]")


def ts(line):
    h, m, s, ms = re.match(r"\[(\d+):(\d+):(\d+),(\d+)\]", line).groups()
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


cues = []
for line in open(PLAIN, encoding="utf-8-sig"):
    if "] " in line:
        cues.append((ts(line), line.split("] ", 1)[1].rstrip("\n")))

for m in json.load(open(MOMENTS, encoding="utf-8")):
    nn = f"{m['nn']:02d}"
    if SEL and nn not in SEL:
        continue
    a, b = m["start"], m["start"] + m["dur"]
    inside = [t for st, t in cues if a - 0.001 <= st < b]
    print(f"=== {nn}  {a:.3f}+{m['dur']:.3f}  ({len(inside)} sentences)")
    for t in inside:
        print("   ", t)
    print()
