"""Scheduler — publishes queued videos (upload_stage7 output) at channel slots.

Usage: python -X utf8 poster.py
    Run every 15 minutes via Windows Task Scheduler (Phase 9 setup).

Reads:
    system\\post_queue.json   entries {video_id, ch_id, status, ...}
    system\\channels.json     per channel: "schedule" + "max_per_day"

Rules per channel:
    schedule "Sat 14:00 UTC" -> only on Sat (UTC), after 14:00 UTC;
    a bare "HH:MM [UTC]" or "daily" runs any day; missing -> any day.
    Each run publishes AT MOST ONE video per channel (15-min stagger) and
    never more than max_per_day for the current UTC date.
    GLOBAL: never more than GLOBAL_MAX_PER_DAY uploads across ALL channels
    per UTC date (free-tier API quota is one shared pool: 5/day total).

Publish = youtube MCP youtube_update_metadata(privacy="public").
Exit 0 = ran fine (empty queue is not an error); exit 1 = a queued channel is
missing from channels.json (STOP — nothing published).
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

from mcp_client import MCPError, call_tool
from routing import queue_path, SYS

DAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}

# Free-tier YouTube API quota: uploads draw from ONE daily pool shared by
# every channel (ecosystem rule: 5 uploads/day total, never pay).
GLOBAL_MAX_PER_DAY = 5


def load_channels():
    """ch_id -> channel def, scanned across all niche groups."""
    path = os.path.join(SYS, "channels.json")
    if not os.path.isfile(path):
        return {}
    out = {}
    for grp in json.load(open(path, encoding="utf-8")).values():
        for c in grp.get("channels", []):
            out[c["id"]] = c
    return out


def parse_schedule(sched):
    """-> (weekday_or_None, HH:MM_or_None). Bare/missing -> (None, None)."""
    if not sched:
        return None, None
    day = None
    for tok in str(sched).replace(",", " ").split():
        t = tok.lower().strip(".")
        if t[:3] in DAYS and day is None:
            day = DAYS[t[:3]]
    tm = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", str(sched))
    hhmm = (int(tm.group(1)), int(tm.group(2))) if tm else None
    return day, hhmm


def main():
    qp = queue_path()
    queue = json.load(open(qp, encoding="utf-8")) if os.path.isfile(qp) else []
    queued = [e for e in queue if e.get("status") == "queued"]
    if not queued:
        print("poster: nothing queued")
        return 0

    chans = load_channels()
    # RULE (non-negotiable): a queued channel must exist in channels.json —
    # checked BEFORE any publish so an undefined channel can never go public.
    unknown = sorted({e["ch_id"] for e in queued} - set(chans))
    if unknown:
        print(f"poster STOP: queued channel(s) {unknown} not in channels.json"
              " — nothing published")
        return 1
    now = datetime.now(timezone.utc)
    today = now.date()

    # Global free-tier cap: uploads posted today across ALL channels.
    posted_global = sum(
        1 for e in queue
        if e.get("status") == "posted"
        and str(e.get("posted_at", ""))[:10] == today.isoformat())

    published = 0
    for ch_id in sorted({e["ch_id"] for e in queued}):
        if posted_global >= GLOBAL_MAX_PER_DAY:
            print(f"poster: global cap {GLOBAL_MAX_PER_DAY}/day reached "
                  "(free tier) — stopping for today")
            break
        cdef = chans.get(ch_id) or {}
        day, hhmm = parse_schedule(cdef.get("schedule"))
        if day is not None and now.weekday() != day:
            continue  # not the scheduled weekday (UTC)
        if hhmm is not None and (now.hour, now.minute) < hhmm:
            continue  # slot not reached yet

        max_per_day = int(cdef.get("max_per_day", 3))
        posted_today = sum(
            1 for e in queue
            if e.get("ch_id") == ch_id
            and e.get("status") == "posted"
            and str(e.get("posted_at", ""))[:10] == today.isoformat())
        if posted_today >= max_per_day:
            continue  # daily cap reached

        # oldest queued entry for this channel — one per channel per run
        entry = min((e for e in queued if e["ch_id"] == ch_id),
                    key=lambda e: e.get("queued_at", ""))
        try:
            txt = call_tool("youtube", "youtube_update_metadata",
                            {"video_id": entry["video_id"], "privacy": "public"},
                            timeout=120)
        except MCPError as e:
            print(f"poster: auth/server error — skipping run ({e})")
            return 0  # transient: leave queued, retry next run
        if txt.startswith("Error"):
            print(f"poster: {entry['video_id']} -> {txt} (left queued)")
            continue
        entry["status"] = "posted"
        entry["posted_at"] = now.isoformat(timespec="seconds")
        published += 1
        posted_global += 1
        print(f"poster: PUBLISHED {entry['ch_id']}/{entry['nn']} "
              f"{entry['video_id']} ({entry.get('title', '')[:60]})")

    with open(qp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(queue, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"poster: published {published}; "
          f"{sum(1 for e in queue if e.get('status') == 'queued')} still queued")
    return 0


if __name__ == "__main__":
    sys.exit(main())
