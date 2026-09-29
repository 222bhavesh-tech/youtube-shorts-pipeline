import re, sys, io

vtt_path, srt_path = sys.argv[1], sys.argv[2]

with io.open(vtt_path, "r", encoding="utf-8-sig") as f:
    lines = f.read().splitlines()

cues = []  # (start_sec, end_sec, text)
i = 0
ts_re = re.compile(r"^(\d{2}):(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[.,](\d{3})")
tag_re = re.compile(r"<[^>]+>")

while i < len(lines):
    m = ts_re.match(lines[i].strip())
    if not m:
        i += 1
        continue
    h1, m1, s1, ms1, h2, m2, s2, ms2 = (int(x) for x in m.groups())
    start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000.0
    end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000.0
    i += 1
    text_lines = []
    while i < len(lines) and lines[i].strip() and "-->" not in lines[i]:
        text_lines.append(lines[i])
        i += 1
    raw = " ".join(text_lines)
    raw = tag_re.sub("", raw)          # strip <c>, word timestamps, etc.
    raw = re.sub(r"\s+", " ", raw).strip()
    if raw:
        cues.append([start, end, raw])

# merge rolling cues: YouTube auto-subs repeat the sentence on a 10ms tail cue
merged = []
for start, end, text in cues:
    if merged and text == merged[-1][2]:
        merged[-1][1] = max(merged[-1][1], end)
        continue
    if merged and text.startswith(merged[-1][2]):
        # continuation grew the same sentence: replace, extend
        merged[-1][1] = max(merged[-1][1], end)
        merged[-1][2] = text
        continue
    if len(text) <= 3 and merged and text in merged[-1][2]:
        merged[-1][1] = max(merged[-1][1], end)
        continue
    merged.append([start, end, text])

def fmt(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms == 1000:
        ms = 0; s += 1
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

with io.open(srt_path, "w", encoding="utf-8", newline="\n") as f:
    for n, (start, end, text) in enumerate(merged, 1):
        if end <= start:
            end = start + 0.5
        f.write(f"{n}\n{fmt(start)} --> {fmt(end)}\n{text}\n\n")

print(f"cues_raw={len(cues)} merged={len(merged)} dur_last={merged[-1][1]:.1f}s")
