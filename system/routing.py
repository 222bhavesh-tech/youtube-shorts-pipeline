"""Shared route.json + channels.json loader for stages 6 and 7.

route.json (project folder, created manually or by system\\download.py):
    {"source_url", "source_channel", "niche", "language", "channels": [...], ...}
channels.json (system\\): {"<niche>_<lang>": {"channels": [{id, ...}]}, ...}

load_route(profile) -> (route, defs_by_id, ch_ids)
Raises ValueError with an actionable message when routing is missing/broken.
"""
import json
import os

SYS = os.path.dirname(os.path.abspath(__file__))


def load_route(profile: dict):
    base = profile["base"]
    route_path = os.path.join(base, "route.json")
    if not os.path.isfile(route_path):
        raise ValueError(
            f"route.json missing: {route_path}  "
            "(create it — see system/download.py or the Nuclear Bunker example)")
    route = json.load(open(route_path, encoding="utf-8"))

    niche = route.get("niche", "extreme")
    lang = route.get("language", profile.get("lang", "en"))
    key = f"{niche}_{lang}"

    chan_path = os.path.join(SYS, "channels.json")
    if not os.path.isfile(chan_path):
        raise ValueError(f"channels.json missing: {chan_path}")
    channels_all = json.load(open(chan_path, encoding="utf-8"))
    if key not in channels_all:
        raise ValueError(f"channels.json has no group '{key}' "
                         f"(available: {sorted(channels_all)})")

    defs = {c["id"]: c for c in channels_all[key].get("channels", [])}
    ch_ids = route.get("channels") or []
    if not ch_ids:
        raise ValueError(f"route.json 'channels' is empty for {key}")
    missing = [c for c in ch_ids if c not in defs]
    if missing:
        raise ValueError(f"channel(s) {missing} not defined in channels.json[{key}]")
    return route, defs, ch_ids


def queue_path() -> str:
    """Global post queue used by upload_stage7 (writer) and poster (reader)."""
    return os.path.join(SYS, "post_queue.json")
