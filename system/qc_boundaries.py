# Boundary QC: does each clip START on a sentence start and END after a sentence end?
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

def is_sent_start(i):
    return i == 0 or cues[i - 1][1].endswith((".", "!", "?", '." ', '!"', '?"'))

starts = [(i, c[0]) for i, c in enumerate(cues)]
bad_start = 0
bad_end = 0
for c in clips:
    # start cue = first cue >= start
    si = next((i for i, t in starts if t >= c["start"] - 0.001), None)
    ok_s = si is not None and is_sent_start(si) and abs(cues[si][0] - c["start"]) < 0.05
    # end: last cue that starts before end; sentence is complete if THAT cue's text
    # ends with punctuation OR the next cue begins within 0.75s after end (audio done)
    li = max((i for i, t in starts if t < c["end"]), default=None)
    end_text = cues[li][1] if li is not None else ""
    nc = cues[li + 1][0] if li is not None and li + 1 < len(cues) else None
    complete = end_text.endswith((".", "!", "?")) or (nc is not None and 0 <= nc - c["end"] <= 0.75)
    if not ok_s:
        bad_start += 1
    if not complete:
        bad_end += 1
    print(f"{c['nn']:02d} start={'OK ' if ok_s else 'MID'} end={'OK ' if complete else 'MID'}"
          f" | prev='{cues[si-1][1][:45] if si and si>0 else ''}'"
          f" | last='{end_text[:45]}' nextcue_dt={round(nc - c['end'], 2) if nc else None}")
print(f"\nbad_starts={bad_start} bad_ends={bad_end}")
