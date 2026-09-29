# Stage 5b helper — measure a clip's SOURCE segment (analysis-only loudnorm
# pass, same -ss/-t input seek as encode_stage4) and store two-pass linear
# values into the profile's "measured" dict for QC loudness-gate failures.
#
# Why (encode_stage4 comments): single-pass loudnorm missed -14 +/-0.6 LU on
# some segments. Two-pass linear needs measured_I/TP/LRA/thresh on that exact
# segment. loudnorm only enters LINEAR_MODE iff BOTH:
#     (measured_TP + gain <= target_TP(-1))  AND  (measured_LRA <= 11)
#   gain = -14 - measured_I
# Presentation rules (mansion 03/13/15 proven cases):
#   - I, TH: always the REAL measured values.
#   - LRA > 11  -> store "11.00": LRA only GATES the mode decision; linear
#     applies pure constant gain and never uses LRA. Real value would keep
#     dynamic mode whose result then fails QC.
#   - TP + gain > -1 -> cap TP at (-1 - gain) ("TP-capped effective value")
#     so linear engages; gain is chosen so output TP lands <= -1.
#   - real values already pass -> store as-is.
# After running: re-encode only the listed NNs (their encNN.ok markers force
# a fresh pass? NO - delete temp\encNN.ok first, then encode_stage4.py <prof> NN ...).
#
# Usage: python measure_loudness.py <profile.json> NN [NN ...]
import json, os, re, subprocess, sys

FFMPEG = (r"C:\Users\bhavesh jeengar\AppData\Local\Microsoft\WinGet\Packages"
          r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe")

KEYS = ("input_i", "input_tp", "input_lra", "input_thresh")
OUT = {"input_i": "I", "input_tp": "TP", "input_lra": "LRA", "input_thresh": "TH"}


def measure(src, start, dur):
    args = [FFMPEG, "-hide_banner", "-nostats",
            "-ss", str(start), "-t", str(dur), "-i", src,
            "-map", "0:a", "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
            "-f", "null", "-"]
    r = subprocess.run(args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    blob = r.stderr or ""
    m = re.search(r"\{[^{}]*\}", blob, re.S)
    if not m or not all(k in m.group(0) for k in KEYS):
        raise SystemExit(f"loudnorm analysis failed rc={r.returncode}: {blob[-500:]}")
    return {k: json.loads(m.group(0))[k] for k in KEYS}


def to_linear(vals):
    I, TP, LRA, TH = (float(vals[k]) for k in ("input_i", "input_tp",
                                               "input_lra", "input_thresh"))
    gain = -14.0 - I
    notes = []
    if TP + gain > -1.0:
        TP = -1.0 - gain
        notes.append(f"TP capped -> {TP:.2f} (gain {gain:+.2f})")
    if LRA > 11.0:
        LRA = 11.0
        notes.append("LRA clamped -> 11.00 (mode gate only)")
    store = {"I": f"{I:.2f}", "TP": f"{TP:.2f}",
             "LRA": f"{LRA:.2f}", "TH": f"{TH:.2f}"}
    return store, notes, gain


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: measure_loudness.py <profile.json> NN [NN ...]")
    prof_path, nns = sys.argv[1], [int(x) for x in sys.argv[2:]]
    prof = json.load(open(prof_path, encoding="utf-8"))
    moments = {m["nn"]: m for m in json.load(open(prof["moments"], encoding="utf-8"))}
    measured = prof.get("measured") or {}
    for nn in nns:
        m = moments[nn]
        real = measure(prof["src"], m["start"], m["dur"])
        store, notes, gain = to_linear(real)
        old = measured.get(str(nn)) or measured.get(nn)
        measured[str(nn)] = store
        print(f"{nn:02d} seg {m['start']}+{m['dur']}: "
              f"I={store['I']} TP={store['TP']} LRA={store['LRA']} TH={store['TH']} "
              f"(real I={real['input_i']} TP={real['input_tp']} LRA={real['input_lra']})"
              + (f" | {'; '.join(notes)}" if notes else " | real passes gating")
              + (f" | was {old}" if old else ""))
    prof["measured"] = measured
    with open(prof_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(prof, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"updated {prof_path} measured={sorted(int(k) for k in measured)}")
    print("now: del temp\\encNN.ok for those NNs, then encode_stage4.py <prof> NN ...")


if __name__ == "__main__":
    main()
