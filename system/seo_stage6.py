"""Stage 6 — per-channel SEO JSONs.

Usage: python -X utf8 seo_stage6.py <profile.json> [NN ...]

Reads the project's route.json (which channels this project goes to) and
system\\channels.json (channel defs), validates every clip's SEO from the
profile meta against the Stage-6 contract, enriches tags ONCE via the local
youtube-seo MCP tool get_tag_analysis (graceful fallback to profile tags),
and writes one JSON per clip per channel:

    <base>\\seo\\<ch_id>\\NN.json
    {nn, ch_id, title, description, desc_lines, tags, category_id, ...}

Stage-6 contract (rules.md — enforced by fail()):
  title <= 100 chars + >= 1 ALL-CAPS word (len > 2)
  description exactly 3 lines; line 3 has 3-5 hashtags incl #Shorts
  tags 10-15; ", ".join(tags) <= 470 chars

Exit: 0 ok, 4 contract/routing failure.
"""
import json
import os
import sys

import src_profile
from mcp_client import call_tool
from routing import load_route

PROF, NNS = src_profile.load(sys.argv[1:])
BASE = PROF["base"]


def fail(msg):
    print("SEO FAILED:", msg)
    sys.exit(4)


def normalize(n):
    n = str(n)
    return f"{int(n):02d}" if n.isdigit() else n


def validate(nn, e):
    """Stage-6 contract; same rules as the profile builders' self-check."""
    t = e.get("title", "")
    if len(t) > 100 or not t.isascii():
        fail(f"{nn}: title len={len(t)} ascii={t.isascii()} — {t!r}")
    if not any(w.isupper() and len(w) > 2 for w in t.split()):
        fail(f"{nn}: title has no ALL-CAPS word (len>2): {t!r}")
    desc = e.get("desc") or []
    if len(desc) != 3:
        fail(f"{nn}: desc must be exactly 3 lines (got {len(desc)})")
    hashes = [w for w in desc[2].split() if w.startswith("#")]
    if not (3 <= len(hashes) <= 5) or "#Shorts" not in hashes:
        fail(f"{nn}: line-3 hashtags {hashes} (need 3-5 incl #Shorts)")
    tags = e.get("tags") or []
    if not (10 <= len(tags) <= 15):
        fail(f"{nn}: tags count {len(tags)} (need 10-15)")
    if len(", ".join(tags)) > 470:
        fail(f"{nn}: joined tags {len(', '.join(tags))} > 470")


def extra_tags(route):
    """One youtube-seo MCP call per project: top tags of the SOURCE channel."""
    src = route.get("source_channel") or ""
    if not src:
        return []
    if src.startswith("@"):
        src = "https://www.youtube.com/" + src  # tool wants a full URL
    try:
        txt = call_tool("youtube-seo", "get_tag_analysis",
                        {"channel_url": src, "limit": 50}, timeout=180)
        data = json.loads(txt)
        tops = data.get("top_tags_by_frequency") or []
        if isinstance(tops, dict):
            tags = list(tops)
        else:
            tags = [t[0] if isinstance(t, (list, tuple)) else t for t in tops]
        out = [t for t in tags if isinstance(t, str) and t.strip()][:20]
        print(f"  MCP get_tag_analysis({src}): {len(out)} candidate tags")
        return out
    except Exception as e:  # noqa: BLE001 — enrichment must never kill SEO
        print(f"  ! get_tag_analysis skipped ({e}) — using profile tags only")
        return []


def merge_tags(base_tags, extra):
    """Base first (authored), then extras; cap 15 tags / 470 joined chars."""
    out = list(base_tags)
    for t in extra:
        if len(out) >= 15:
            break
        tl = t.lower().strip()
        if not tl or any(tl == b.lower() for b in out):
            continue
        cand = out + [t.strip()]
        if len(", ".join(cand)) > 470:
            continue
        out.append(t.strip())
    return out


def main():
    meta = PROF.get("meta") or {}
    if not meta:
        fail("profile has no meta (titles/descs/tags)")
    try:
        route, defs, ch_ids = load_route(PROF)
    except ValueError as e:
        fail(str(e))

    allnn = sorted(normalize(n) for n in meta)
    sel = [normalize(n) for n in NNS] or allnn
    bad = [n for n in sel if n not in allnn]
    if bad:
        fail(f"unknown clip(s) {bad} (profile has {allnn})")

    extra = extra_tags(route)
    lang = route.get("language", PROF.get("lang", "en"))

    written = 0
    for cid in ch_ids:
        cdef = defs[cid]
        outdir = os.path.join(BASE, "seo", cid)
        os.makedirs(outdir, exist_ok=True)
        for nn in sel:
            e = meta[int(nn)]
            tags = merge_tags(e.get("tags") or [], extra)
            if not (10 <= len(tags) <= 15):
                fail(f"{nn}: merged tags {len(tags)} (need 10-15)")
            doc = {
                "nn": nn,
                "ch_id": cid,
                "title": e["title"],
                "description": "\n".join(e["desc"]),
                "desc_lines": list(e["desc"]),
                "tags": tags,
                "category_id": str(cdef.get("category_id", 22)),
                "language": lang,
                "audience": cdef.get("audience"),
                "style": cdef.get("style"),
                "privacy": "private",
            }
            validate(nn, e)  # authored SEO must stand on its own
            with open(os.path.join(outdir, f"{nn}.json"), "w",
                      encoding="utf-8", newline="\n") as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
                f.write("\n")
            written += 1
    print(f"SEO OK: {written} files "
          f"({len(sel)} clips x {len(ch_ids)} channel(s)) -> {os.path.join(BASE, 'seo')}")


if __name__ == "__main__":
    main()
