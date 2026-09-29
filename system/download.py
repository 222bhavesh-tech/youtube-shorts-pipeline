r"""
Usage: python system\download.py <URL_or_path> --niche extreme --lang en --channels test
Downloads 4K + EN/HI audio (rejects if neither). Creates project folder + route.json.
"""
import subprocess, sys, os, json
from datetime import datetime


def get_audio_languages(url):
    """Check available audio languages via yt-dlp."""
    r = subprocess.run(
        ["yt-dlp", "--list-soundtracks", "--no-download", url],
        capture_output=True, text=True
    )
    # Parse output for 'en', 'hi'
    # Fallback: check --list-subs or stream tags
    langs = set()
    if "en" in r.stdout.lower():
        langs.add("en")
    if "hi" in r.stdout.lower():
        langs.add("hi")
    return langs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    url = sys.argv[1]
    niche = get_flag("--niche")
    lang = get_flag("--lang")
    channels_raw = get_flag("--channels") or ""
    channels = [c for c in channels_raw.split(",") if c]
    if not niche or not lang:
        print("✗ --niche and --lang are required "
              "(e.g. --niche extreme --lang en --channels test)")
        sys.exit(2)

    BASE = r"D:\youtube system"

    if url.startswith("http"):
        # YouTube path: check audio
        langs = get_audio_languages(url)
        if "en" not in langs and "hi" not in langs:
            print(f"✗ REJECTED: no EN/HI audio found (got: {langs})")
            sys.exit(1)
        tracks = [l for l in ["en", "hi"] if l in langs]
        print(f"  Audio tracks: {tracks}")

        # Download 4K video + selected audio
        cmd = ["yt-dlp", "-f", "bestvideo[height<=2160]+bestaudio",
               "--merge-output-format", "mp4",
               "-o", f"{BASE}\\output\\4k video\\{lang}\\%(title)s.%(ext)s",
               url]
        subprocess.run(cmd, check=True)
    else:
        # FunClip path (movie/series): you provide local path
        print(f"  Local file: {url} (FunClip path — no download)")
        tracks = ["en"]  # or detect from file

    # Create project folder
    project_name = get_project_name(url)  # from title or filename
    project_dir = os.path.join(BASE, "output", "final clips", niche, lang, project_name)
    os.makedirs(os.path.join(project_dir, "clips"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "ass"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "seo"), exist_ok=True)

    # Write route.json
    route = {
        "source_url": url,
        "niche": niche,
        "language": lang,
        "channels": channels,
        "audio_tracks": tracks,
        "routed_at": datetime.now().isoformat(timespec="seconds"),
        "routed_by": "manual"
    }
    with open(os.path.join(project_dir, "route.json"), "w", encoding="utf-8") as f:
        json.dump(route, f, indent=2)

    print(f"✓ Project: {project_dir}")
    print(f"✓ Routed to: {channels}")
    print(f"✓ Audio: {tracks}")


def get_flag(name):
    if name in sys.argv:
        idx = sys.argv.index(name) + 1
        if idx < len(sys.argv):
            return sys.argv[idx]
    return None


def get_project_name(url):
    # Extract from URL title or filename
    if os.path.isfile(url):
        return os.path.splitext(os.path.basename(url))[0]
    return "New Project"  # TODO: use yt-dlp --print title


if __name__ == "__main__":
    main()
