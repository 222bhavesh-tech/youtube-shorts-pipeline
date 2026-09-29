# Slice en\plain.txt per clip range -> print for metadata / hook authoring.
# Usage: python slice_transcript.py [plain] [moments] [hook_pattern]
#   hook_pattern default "hook{nn:02d}.txt" (temp root, written by prep_stage4);
#   pass "-" to skip the hook column (pre-prep authoring, avoids stale hooks).
import json, os, re, sys

PROJ = r"D:\youtube system"
PLAIN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJ, "output", "transcript", "en", "plain.txt")
MOM = sys.argv[2] if len(sys.argv) > 2 else os.path.join(PROJ, "output", "temp", "moments_tnTP.json")
HOOKPAT = sys.argv[3] if len(sys.argv) > 3 else "hook{nn:02d}.txt"

def ts_to_sec(ts):
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

lines = []
for raw in open(PLAIN, encoding="utf-8"):
    m = re.match(r"\[(\d{2}:\d{2}:\d{2},\d{3})\]\s*(.*)", raw.strip())
    if m:
        lines.append((ts_to_sec(m.group(1)), m.group(2)))

moments = json.load(open(MOM, encoding="utf-8"))
for mo in moments:
    nn, a, b = mo["nn"], mo["start"], mo["end"]
    hook = "(no hook yet)"
    if HOOKPAT != "-":
        hp = os.path.join(PROJ, "output", "temp", HOOKPAT.format(nn=nn))
        if os.path.exists(hp):
            hook = open(hp, encoding="utf-8").read().strip()
    print(f"=== {nn:02d} [{a:.1f}-{b:.1f}] HOOK: {hook}")
    for t, x in lines:
        if a <= t < b:
            print(f"  {t - a:5.1f} {x}")
    print()
