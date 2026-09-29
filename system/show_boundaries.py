# Show sentence-start cues (text) within +-12s of each clip boundary for hook review.
import json

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
        cues.append([round(t, 3), text])

sent = [cues[0]] + [cues[i] for i in range(1, len(cues))
                    if cues[i - 1][1].endswith((".", "!", "?"))]

bounds = [c["start"] for c in clips] + [clips[-1]["end"]]
for b in bounds:
    print(f"\n=== boundary {b:.3f} ===")
    for t, txt in sent:
        if b - 6 <= t <= b + 12:
            mark = ">>" if abs(t - b) < 0.05 else "  "
            print(f" {mark} {t:8.3f}  {txt[:80]}")
