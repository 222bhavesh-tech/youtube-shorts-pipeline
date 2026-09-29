"""Pipeline runner — prep -> encode -> qc -> SEO -> thumbnails -> [upload].

Usage: python -X utf8 system\\run_pipeline.py <profile.json> [NN ...] [--upload]

    NN        optional clip numbers (e.g. 01) — stages receive them and
              process only those clips (full run = omit).
    --upload  only with an explicit human upload pass; without it stage 7
              is skipped with "[SKIP] Upload — use --upload after your pass".

Stages run with cwd=output\\temp (encode contract). Exit codes:
    1=prep  2=encode  3=qc  4=seo  5=upload  6=usage  7=route

NOTE: the encode stages create video files — do NOT run while the
"no create any video" pause is active.
"""
import json
import os
import subprocess
import sys

import routing
import src_profile

PROJ = r"D:\youtube system"
SYS = os.path.dirname(os.path.abspath(__file__))
TEMP = os.path.join(PROJ, "output", "temp")


def run(stage, args):
    cmd = [sys.executable, "-X", "utf8", os.path.join(SYS, stage), *args]
    print(f"[RUN] {stage} {' '.join(a.rsplit(os.sep, 1)[-1] for a in args)}",
          flush=True)
    return subprocess.call(cmd, cwd=TEMP)


def autocommit(stage, prof):
    """RULE (non-negotiable): auto-commit after each stage."""
    msg = (f"chore(pipeline): {os.path.splitext(os.path.basename(stage))[0]} ok "
           f"({os.path.basename(prof)})")
    try:
        subprocess.run(["git", "add", "-A"], cwd=PROJ, capture_output=True,
                       text=True, errors="replace", check=False)
        r = subprocess.run(["git", "commit", "-m", msg], cwd=PROJ,
                           capture_output=True, text=True, errors="replace")
    except OSError as e:
        print("[git] auto-commit skipped:", e)
        return
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    if r.returncode == 0:
        print("[git]", msg)
    elif "nothing to commit" in out:
        print("[git] nothing to commit")
    else:
        print("[git] auto-commit failed:", out[-200:])


def main():
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 6
    upload = "--upload" in argv
    argv = [a for a in argv if a != "--upload"]
    prof = os.path.abspath(argv[0])
    if not os.path.isfile(prof):
        print("profile not found:", prof)
        return 6
    # RULE (non-negotiable): route.json must exist or stop — checked BEFORE
    # any stage so an unroutable project never burns GPU time.
    try:
        pdef, _ = src_profile.load([prof])
        routing.load_route(pdef)
    except Exception as e:  # missing/broken route.json or channels.json
        print("ROUTE CHECK FAILED:", e)
        return 7
    nn = argv[1:]
    pas = [prof, *nn]

    for stage, code in (("prep_stage4.py", 1),
                        ("encode_stage4.py", 2),
                        ("qc_stage5.py", 3)):
        rc = run(stage, pas)
        if rc != 0:
            print(f"{stage.upper()} FAILED rc={rc}"
                  + ("  (loudness fail? measure_loudness.py <profile> NN -> "
                     "delete encNN.ok -> re-encode)" if code == 3 else ""))
            return code
        autocommit(stage, prof)

    rc = run("seo_stage6.py", pas)
    if rc != 0:
        print("SEO FAILED")
        return 4
    autocommit("seo_stage6.py", prof)

    run("thumb_gen.py", [prof])  # thumbnails — best-effort, rc ignored
    autocommit("thumb_gen.py", prof)

    if upload:
        rc = run("upload_stage7.py", pas)
        if rc != 0:
            print("UPLOAD FAILED")
            return 5
        autocommit("upload_stage7.py", prof)
    else:
        print("[SKIP] Upload — use --upload after your pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
