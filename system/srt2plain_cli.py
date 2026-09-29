import re, sys
src = sys.argv[1]
out = sys.argv[2]
txt = open(src, encoding="utf-8-sig").read()
blocks = re.split(r"\n\s*\n", txt.strip())
lines = []
pat = re.compile(r"^(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})")
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
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("wrote", len(lines), "lines ->", out)
