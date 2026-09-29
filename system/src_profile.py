# Per-source profile loader — ONE JSON per source drives prep_stage4 /
# encode_stage4 / qc_stage5 / meta_stage6 (and slice_transcript args).
# No profile arg -> legacy grocery (tnTP) defaults (identical old behavior).
#
# Usage:  python <stage>.py [profile.json] [NN ...]     (profile optional)
#         python <stage>.py [NN ...]                    (legacy default)
#
# Profile keys (all optional; merge over GROCERY defaults):
#   src      source video path
#   lang     "en" | "hi"  -> face_track/<lang> subdir
#   plain    transcript plain.txt path (ALWAYS EN per caption policy)
#   moments  select_moments output JSON
#   tag      face_track filename tag
#   base     final clips output dir (clips\ ass\ metadata\ live under it)
#   hooks    {nn: "HOOK TEXT"}        authored (prep_stage4 drawtext)
#   slugs    {nn: "url-slug"}         authored (clip filenames)
#   meta     {nn: {title,desc,tags}}  authored (meta_stage6 validation+write)
# JSON object keys arrive as strings -> normalized to int here.
import json, os

PROJ = r"D:\youtube system"
TEMP = os.path.join(PROJ, "output", "temp")

GROCERY = {
    "lang": "hi",
    "src": r"D:\youtube system\output\4k video\hi\$10,000 Every Day You Survive In A Grocery Store [tnTPaLOaHz8].webm",
    "plain": os.path.join(PROJ, "output", "transcript", "en", "plain.txt"),
    "moments": os.path.join(TEMP, "moments_tnTP.json"),
    "tag": "$10,000 Grocery Store",
    "base": os.path.join(PROJ, "output", "final clips", "extreme", "hi",
                         "$10,000 Every Day You Survive In A Grocery Store [tnTPaLOaHz8]"),
}

def load(argv):
    """argv = [profile.json] [NN ...] | [NN ...].
    Returns (profile, rest_of_argv_without_profile_path)."""
    args = list(argv)
    prof = dict(GROCERY)
    if args and args[0].lower().endswith(".json"):
        prof.update(json.load(open(args[0], encoding="utf-8")))
        args = args[1:]
    for k in ("hooks", "slugs", "meta", "measured"):
        if isinstance(prof.get(k), dict):
            prof[k] = {int(kk): vv for kk, vv in prof[k].items()}
    prof.setdefault("fdir", os.path.join(PROJ, "output", "face_track", prof["lang"]))
    return prof, args
