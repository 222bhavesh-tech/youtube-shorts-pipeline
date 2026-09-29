# Stage 3 QC: print first cue (hook) + last cue inside each selected clip.
import json, re

PLAIN = r"D:\youtube system\output\transcript\en\plain.txt"
MOMENTS = r"D:\youtube system\output\temp\moments_tnTP.json"

clips = json.load(open(MOMENTS))
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
        cues.append((round(t, 3), text))

for c in clips:
    inside = [x for x in cues if c["start"] <= x[0] < c["end"]]
    first = inside[0][1] if inside else "(none)"
    last = inside[-1][1] if inside else "(none)"
    print(f"{c['nn']:02d} [{c['start']:7.1f}-{c['end']:7.1f}]")
    print(f"    HOOK: {first}")
    print(f"    END : {last}")
