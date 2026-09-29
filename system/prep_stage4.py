# Stage 4 prep — per clip: face_track_analyze.py + gen_ass.py + hookNN.txt
# Usage: python prep_stage4.py [NN ...]   (default: all 15 from moments_tnTP.json)
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

PROJ = r"D:\youtube system"
SYS  = os.path.join(PROJ, "system")
TEMP = os.path.join(PROJ, "output", "temp")
import src_profile
PROF, ARGS = src_profile.load(sys.argv[1:])
SRC  = PROF["src"]
FDIR = PROF["fdir"]
TAG  = PROF["tag"]
BASE = PROF["base"]
MOMENTS = PROF["moments"]
PLAIN   = PROF["plain"]
PY = sys.executable

# Hook Title Rule: unique per clip, max 8 words, ALL CAPS, segment's most shocking line.
# Clip 01 = main video title only.
HOOKS = {
 1: "$10,000 EVERY DAY IN A GROCERY STORE",
 2: "A LOT OF ELECTRONICS OVER THERE",
 3: "THEY'RE GOING TO GO BAD VERY FAST",
 4: "I'M GOING TO BUILD A WALL",
 5: "I NEVER THOUGHT I'D SEE THIS",
 6: "SCANNING AWAY FOR ANOTHER 10K",
 7: "THE DAYS STARTED BLENDING TOGETHER",
 8: "I MADE A RACE CAR TRACK",
 9: "I HAD ORIGINALLY $60,000 READY TO GO",
10: "I GOT $360,000",
11: "I CAN ACTUALLY HANG OUT IN HERE AGAIN",
12: "IT'S FREEZING",
13: "HOW DOES ONE BUST A POOL?",
14: "ARE YOU THERE, JIMMY?",
15: "LET'S GO LOOK AT YOUR SEA OF MONEY",
}
HOOKS = PROF.get("hooks") or HOOKS   # profile-authored hooks override legacy

def run(args, cwd=SYS):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def face(m):
    nn = f"{m['nn']:02d}"
    crop  = os.path.join(FDIR, f"{TAG}_crop{nn}.txt")
    track = os.path.join(FDIR, f"{TAG}_track{nn}.json")
    if os.path.exists(crop) and os.path.exists(track):
        return f"{nn} face-track: exists"
    rc, out = run([PY, "face_track_analyze.py", str(m["start"]), str(m["dur"]), nn,
                   SRC, FDIR, TAG])
    ok = os.path.exists(crop) and os.path.exists(track) and os.path.getsize(crop) > 100
    return f"{nn} face-track: {'ok' if ok else 'FAIL rc=' + str(rc)}"

def ass_and_hook(m):
    nn = f"{m['nn']:02d}"
    a = os.path.join(TEMP, f"{nn}.ass")
    rc, out = run([PY, os.path.join(SYS, "gen_ass.py"), str(m["start"]), str(m["end"]), a, PLAIN])
    if rc != 0 or not os.path.exists(a):
        return f"{nn} ass: FAIL rc={rc} {out[-200:]}"
    # copy ASS to final ass\ folder (outputs live under final clips only)
    adir = os.path.join(BASE, "ass"); os.makedirs(adir, exist_ok=True)
    with open(a, encoding="utf-8-sig") as f: txt = f.read()
    with open(os.path.join(adir, f"{nn}.ass"), "w", encoding="utf-8-sig") as f:
        f.write(txt)
    # hook title -> temp\hookNN.txt (textfile= drawtext, NO trailing newline)
    h = HOOKS[m["nn"]]
    with open(os.path.join(TEMP, f"hook{nn}.txt"), "w", encoding="utf-8", newline="") as f:
        f.write(h)
    return f"{nn} ass+hook: ok ({len(h)} chars: {h})"

def main():
    moments = json.load(open(MOMENTS, encoding="utf-8"))
    if ARGS:
        sel = set(ARGS)
        moments = [m for m in moments if f"{m['nn']:02d}" in sel]
    print(f"prep: {len(moments)} clips, face-track workers=2", flush=True)
    with ThreadPoolExecutor(max_workers=2) as ex:
        for r in ex.map(face, moments):
            print(r, flush=True)
    fails = 0
    for m in moments:
        r = ass_and_hook(m)
        if "FAIL" in r: fails += 1
        print(r, flush=True)
    print(f"prep done, fails={fails}", flush=True)
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
