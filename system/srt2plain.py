import re
src = r"D:\youtube system\output\transcript\en\7 Days Exploring An Underground City [bn0Kh9c4Zv4].en.srt"
out = r"D:\youtube system\output\transcript\en\plain_bn0.txt"
txt = open(src, encoding="utf-8-sig").read()
blocks = re.split(r"\n\s*\n", txt.strip())
lines = []
pat = re.compile(r"^(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})")
n = 0
for b in blocks:
    ls = [l for l in b.splitlines() if l.strip()]
    if not ls:
        continue
    m = None
    ti = None
    for i, l in enumerate(ls):
        m = pat.match(l)
        if m:
            ti = i
            break
    if not m:
        continue
    content = " ".join(ls[ti + 1:]).strip()
    if not content:
        continue
    lines.append("[%s] %s" % (m.group(1), content))
    n += 1
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("wrote", n, "lines ->", out)
