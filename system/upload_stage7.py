"""Stage 7 — upload through the local YouTube MCP server.

Usage: python -X utf8 upload_stage7.py <profile.json> [NN ...]

    (normally gated: run_pipeline.py <profile> --upload)

Flow per channel in route.json:
    youtube_whoami -> youtube_upload (PRIVATE) -> youtube_playlist_add
    -> youtube_seo_audit -> append system\\post_queue.json (for poster.py)

NEVER run this without an explicit human upload pass (rules: no upload
until the user passes; branding/scope/titles must be settled first).
Every video goes up PRIVATE; publishing is poster.py's job, not this file.

Exit: 0 ok, 5 failure.
"""
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone

import src_profile
from mcp_client import MCPError, call_tool
from routing import load_route, queue_path

PROF, NNS = src_profile.load(sys.argv[1:])
BASE = PROF["base"]
CLIPS = os.path.join(BASE, "clips")
PREVIEW = r"D:\youtube system\output\temp\preview"


def fail(msg):
    print("UPLOAD FAILED:", msg)
    sys.exit(5)


def normalize(n):
    n = str(n)
    return f"{int(n):02d}" if n.isdigit() else n


def mcp(server, tool, args=None, timeout=180):
    try:
        txt = call_tool(server, tool, args, timeout=timeout)
    except MCPError as e:
        fail(f"{tool}: {e}")
    if txt.startswith("Error") or txt.startswith("No channel"):
        fail(f"{tool}: {txt}")
    return txt


def save_route(route, route_path):
    with open(route_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(route, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    try:
        route, defs, ch_ids = load_route(PROF)
    except ValueError as e:
        fail(str(e))
    route_path = os.path.join(BASE, "route.json")

    seo_dir = os.path.join(BASE, "seo")
    allnn = sorted(normalize(n) for n in (PROF.get("meta") or {}))
    sel = [normalize(n) for n in NNS] or allnn
    bad = [n for n in sel if n not in allnn]
    if bad:
        fail(f"unknown clip(s) {bad} (profile has {allnn})")

    # queue file (poster reads it; create now so the shape is stable)
    qp = queue_path()
    queue = json.load(open(qp, encoding="utf-8")) if os.path.isfile(qp) else []

    # 1) whoami once — proves auth before any upload
    who = mcp("youtube", "youtube_whoami", timeout=120)
    try:
        w = json.loads(who)
        print(f"whoami: {w.get('title')} (subs={w.get('subscribers')}, "
              f"thumbs={'yes' if w.get('custom_thumbnails') else 'no/' + str(w.get('thumbnail_verified'))})")
    except json.JSONDecodeError:
        print("whoami:", who.replace("\n", " ")[:200])

    total = 0
    for cid in ch_ids:
        # 2) project playlist per channel (created once, cached in route.json)
        plids = route.setdefault("playlist_ids", {})
        plid = plids.get(cid)
        if not plid:
            created = mcp("youtube", "youtube_playlist_create", {
                "title": PROF.get("tag", "Shorts"),
                "description": f"{PROF.get('tag', '')} — auto playlist",
                "privacy": "public"}, timeout=120)
            plid = json.loads(created)["playlist_id"]
            plids[cid] = plid
            save_route(route, route_path)
            print(f"  playlist created for {cid}: {plid}")

        for nn in sel:
            seo_file = os.path.join(seo_dir, cid, f"{nn}.json")
            if not os.path.isfile(seo_file):
                fail(f"SEO missing: {seo_file} — run seo_stage6.py first")
            seo = json.load(open(seo_file, encoding="utf-8"))

            mp4 = glob.glob(os.path.join(CLIPS, f"{nn}_*.mp4"))
            if not mp4:
                fail(f"no clip mp4 for {nn} in {CLIPS}")

            thumb = os.path.join(PREVIEW, f"{nn}_thumb.jpg")
            args = {
                "file_path": mp4[0],
                "title": seo["title"],
                "description": seo["description"],
                "tags": seo["tags"],
                "category_id": seo.get("category_id", "22"),
                "privacy": "private",
                "thumbnail_path": thumb if os.path.isfile(thumb) else None,
            }
            args = {k: v for k, v in args.items() if v is not None}

            print(f"  upload {cid}/{nn}: {seo['title']}")
            res = mcp("youtube", "youtube_upload", args, timeout=1800)
            try:
                vid = json.loads(res)["video_id"]
            except (json.JSONDecodeError, KeyError):
                m = re.search(r"\b[A-Za-z0-9_-]{11}\b", res)
                if not m:
                    fail(f"cannot parse video id from: {res[:200]}")
                vid = m.group(0)

            mcp("youtube", "youtube_playlist_add",
                {"playlist_id": plid, "video_id": vid}, timeout=120)

            audit = mcp("youtube", "youtube_seo_audit",
                        {"video_id": vid}, timeout=120)
            sm = re.search(r'"score"\s*:\s*(\d+)', audit)
            score = int(sm.group(1)) if sm else None
            flag = "" if (score is None or score >= 80) else "  << WARN: score < 80"
            print(f"    vid={vid}  seo_audit={score if score is not None else '?'}{flag}")

            queue.append({
                "video_id": vid,
                "ch_id": cid,
                "nn": nn,
                "profile": os.path.basename(sys.argv[1]) if len(sys.argv) > 1 else "",
                "tag": PROF.get("tag"),
                "title": seo["title"],
                "status": "queued",
                "queued_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
            total += 1

    with open(qp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(queue, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"UPLOAD OK: {total} video(s) private + playlisted; "
          f"{total} queued in {qp} (poster.py publishes)")


if __name__ == "__main__":
    main()
