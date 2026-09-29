r"""
Usage: python system\thumb_gen.py system\profiles\bunker.json
Extracts the face-zoom PEAK frame -> 1280x720 JPEG per clip.

Peak time = the sample with the largest face height (fh) in the matching
face_track/<lang>/<tag>_trackNN.json (samples: [{t, cx, fh, diff}, ...]).
Track files are filtered by the profile "tag" — 4+ sources share trackNN
numbers in face_track/en, so an unfiltered glob would pick the wrong one.
"""
import json, os, glob, subprocess, sys

PROFILE = sys.argv[1]
BASE = r"D:\youtube system"
# Production ffmpeg (PATH ffmpeg = old FunClip build — env quirk MM-YT-ENV-QUIRKS)
FFMPEG = (r"C:\Users\bhavesh jeengar\AppData\Local\Microsoft\WinGet\Packages"
          r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
          r"\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe")


def main():
    prof = json.load(open(PROFILE, encoding="utf-8"))
    # base may be absolute (bunker.json) or repo-relative
    base_path = prof["base"] if os.path.isabs(prof["base"]) else os.path.join(BASE, prof["base"])
    clips_dir = os.path.join(base_path, "clips")
    preview_dir = os.path.join(BASE, "output", "temp", "preview")
    os.makedirs(preview_dir, exist_ok=True)

    lang = prof.get("lang", "en")
    tag = prof.get("tag", "")
    # clip NNs live in the hooks dict ("1".."15" -> zero-padded file prefixes)
    nns = sorted(prof.get("hooks", {}).keys(), key=int)

    ffmpeg = FFMPEG if os.path.isfile(FFMPEG) else "ffmpeg"

    for nn_key in nns:
        nn = f"{int(nn_key):02d}"

        # peak face-zoom time from trackNN.json samples (fh = face height px)
        peak_time = 3.0  # fallback: 3s in
        tracks = glob.glob(os.path.join(BASE, "output", "face_track", lang, f"*track{nn}.json"))
        if tag:
            tagged = [t for t in tracks if tag.lower() in os.path.basename(t).lower()]
            tracks = tagged or tracks
        if tracks:
            track = json.load(open(tracks[0], encoding="utf-8"))
            samples = [s for s in track.get("samples", []) if s.get("fh")]
            if samples:
                peak_time = max(samples, key=lambda s: s["fh"])["t"]

        # clip file: NN_slug.mp4
        mp4 = glob.glob(os.path.join(clips_dir, f"{nn}_*.mp4"))
        if not mp4:
            print(f"  ✗ {nn} — no mp4")
            continue

        out = os.path.join(preview_dir, f"{nn}_thumb.jpg")
        r = subprocess.run([
            ffmpeg, "-y", "-ss", str(peak_time),
            "-i", mp4[0], "-frames:v", "1",
            "-vf", "scale=1280:720",
            "-q:v", "2", out
        ], capture_output=True)
        if r.returncode == 0:
            print(f"  ✓ {nn}_thumb.jpg (t={peak_time:.1f}s)")
        else:
            print(f"  ✗ {nn} — ffmpeg rc={r.returncode}")

    print(f"\n✓ Thumbnails in {preview_dir}")


if __name__ == "__main__":
    main()
