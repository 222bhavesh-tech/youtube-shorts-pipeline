# Builds system\profiles\g3.json for the I Survived Extreme Places v2 run.
# Authoring source: output\temp\g3_clipdump.txt (814 lines, 15 windows
# from moments_g3.json over plain_g3.txt).
#   tag  = "I Survived Extreme Places v2"  (legacy face_track\en files are
#          "I Survived Extreme Places_crop/trackNN" -> v2 suffix avoids skip-if)
#   base = final clips\extreme\en\I Survived Extreme Places\v2  (legacy
#          14-clip folder untouched; three legacy sources all use a v2 subfolder)
#   measured = {}  (never inherit legacy MEASURED)
# Hooks: <=8 words, ALL CAPS, unique, most shocking line; clip 01 = title.
import json, os

PROJ = r"D:\youtube system"

hooks = {
    1: "THREE BIOMES THAT WANT US DEAD",      # clip 01 = main video title
    2: "OUR DANGER IS LITERALLY DEATH",
    3: "HE BUILT A BRIDGE TO SAVE HIS WIFE",
    4: "CAMPING EARLY COULD LOSE US THE RACE",
    5: "WE FOUND A SKELETON IN THE WILDERNESS",
    6: "THE BIGGEST MISTAKE OF THIS VIDEO",
    7: "A RAFT ACROSS A RIVER OF ANACONDAS",
    8: "WE SPY ON OUR RIVALS ALL NIGHT",
    9: "I ASKED AI HOW TO BUILD A RAFT",
    10: "A GIANT SHARK TOOTH IN THE DESERT",
    11: "THE CRAZIEST THING I'VE EVER DONE",
    12: "WE MISSED THE LAND BY TWO MILES",
    13: "WE LEFT OUR TENT TO WIN THE RACE",
    14: "JIMMY THREW UP FROM PURE EXHAUSTION",
    15: "A 50 MPH STORM STOPPED THE FINISH",
}

slugs = {
    1: "three-deadly-biomes",
    2: "our-danger-is-death",
    3: "bridge-for-his-wife",
    4: "camping-early-mistake",
    5: "skeleton-in-the-wild",
    6: "dumping-the-supplies",
    7: "raft-over-anacondas",
    8: "spying-all-night",
    9: "ai-built-our-raft",
    10: "shark-tooth-in-desert",
    11: "swept-down-the-river",
    12: "two-miles-off-course",
    13: "all-night-mountain-push",
    14: "jimmy-threw-up",
    15: "storm-at-the-finish",
}

TAGS = ["shorts", "viral shorts", "youtube shorts", "mrbeast",
        "extreme challenge", "survival race", "jungle survival",
        "desert survival", "antarctic survival", "helicopter race",
        "extreme places", "survival challenge"]

# one clip-specific tag rides in front of the shared 12 (13 total <= 15)
SPECIFIC = {
    1: "biome survival race", 2: "antarctic blizzard", 3: "amazon bridge",
    4: "desert dunes", 5: "wilderness skeleton", 6: "survival gear drop",
    7: "river raft build", 8: "night race strategy", 9: "ai raft build",
    10: "desert shark tooth", 11: "river crossing", 12: "race standings",
    13: "night mountain hike", 14: "sandstorm survival", 15: "50 mph wind",
}

meta = {
    1: {"title": "I SURVIVED The Most Extreme Places On Earth #shorts",
        "desc": ["Three teams dropped into a jungle, a desert, and Antarctica - first to the helicopter wins $100,000 for their moms.",
                 "No gear, no crew, just a map and a race where everything tries to kill you.",
                 "#Shorts #ExtremeSurvival #SurvivalRace #MrBeast"],
        "tags": [SPECIFIC[1]] + TAGS},
    2: {"title": "Their Team Was Only 2% Done In A BLIZZARD #shorts",
        "desc": ["Zero visibility, frozen toes, and a team sitting at just 2% of the race.",
                 "With the trail gone, setting up camp immediately might be their only shot at surviving the night.",
                 "#Shorts #Antarctic #BlizzardSurvival #ExtremeChallenge"],
        "tags": [SPECIFIC[2]] + TAGS},
    3: {"title": "He Built A BRIDGE Across The Amazon #shorts",
        "desc": ["One fallen log, a rope, and a husband who refused to let his wife get soaked.",
                 "A filter bottle makes the river drinkable - but they are still only 10% of the way to rescue.",
                 "#Shorts #AmazonJungle #SurvivalBuild #ExtremeChallenge"],
        "tags": [SPECIFIC[3]] + TAGS},
    4: {"title": "They're In FIRST Place But Made A TERRIBLE Mistake #shorts",
        "desc": ["Dune after dune, 35 pounds of water each - and they just took the lead.",
                 "Then they did the one thing you never do in a race: stopped to camp while rivals kept walking.",
                 "#Shorts #DesertSurvival #RaceDrama #ExtremeChallenge"],
        "tags": [SPECIFIC[4]] + TAGS},
    5: {"title": "They Found A SKELETON While Losing The Race #shorts",
        "desc": ["Deep in the canyon, a skull has them guessing animal or human.",
                 "One quarter of the race done - and for the first time, Jimmy's team has the lead.",
                 "#Shorts #Skeleton #WildernessRace #MrBeast"],
        "tags": [SPECIFIC[5]] + TAGS},
    6: {"title": "They Threw Away 32 Pounds Of SUPPLIES #shorts",
        "desc": ["Four eight-pound packs are slowing them down - so they dump the weight.",
                 "It might be the biggest mistake of the video. Night falls and the tent fight begins.",
                 "#Shorts #SurvivalMistake #JungleRace #ExtremeChallenge"],
        "tags": [SPECIFIC[6]] + TAGS},
    7: {"title": "Their Next Move: A RAFT Filled With Anacondas #shorts",
        "desc": ["Camp is set on the river - tomorrow they build a raft and sail through piranhas and anacondas.",
                 "FaceTime across the teams reveals the standings: 40%, 33%, and a shocking 7%.",
                 "#Shorts #RaftBuild #AmazonRace #SurvivalChallenge"],
        "tags": [SPECIFIC[7]] + TAGS},
    8: {"title": "They Woke Up FIRST And Took A Head Start #shorts",
        "desc": ["All night in the tent, watching the tracker to make sure nobody moves without them.",
                 "Sunrise brings clear skies and an oasis - but that current is far too strong to swim.",
                 "#Shorts #HeadStart #RiverRace #ExtremeChallenge"],
        "tags": [SPECIFIC[8]] + TAGS},
    9: {"title": "They Asked AI To Build Their RAFT #shorts",
        "desc": ["Bamboo, rope, and a survival plan straight from an AI chatbot.",
                 "Then comes the gamble: a shortcut so risky it could cost them the entire challenge.",
                 "#Shorts #AISurvival #RaftBuild #ExtremeChallenge"],
        "tags": [SPECIFIC[9]] + TAGS},
    10: {"title": "A GIANT Shark Tooth Found In The Desert?! #shorts",
         "desc": ["The Peruvian desert was once a shallow ocean - and they just found the proof.",
                  "Zip ties become raft genius, and the Arctic team suddenly takes the lead.",
                  "#Shorts #SharkTooth #DesertFind #SurvivalRace"],
         "tags": [SPECIFIC[10]] + TAGS},
    11: {"title": "Their RAFT Is At The Mercy Of The Current #shorts",
         "desc": ["One tiny raft, three people, and a river that refuses to let them stop.",
                  "Bags ride on Thea while the others get drenched, kicking with everything they have.",
                  "#Shorts #RiverRaft #DangerousRace #SurvivalChallenge"],
         "tags": [SPECIFIC[11]] + TAGS},
    12: {"title": "Missing This Spot Cost Them TWO MILES #shorts",
         "desc": ["One wrong landing and the shortcut became a longcut - two miles downriver.",
                  "Legs shaking on shore, the standings read 58%, 47%, 40% - anyone's game.",
                  "#Shorts #RiverRace #Comeback #ExtremeChallenge"],
         "tags": [SPECIFIC[12]] + TAGS},
    13: {"title": "They Abandoned Their Tent For An ALL-NIGHT Push #shorts",
         "desc": ["Drop the tent, keep the sleeping bag, and walk all night to the helicopter.",
                  "A mountain stands between them and extraction - knees shaking, a storm rolling in.",
                  "#Shorts #NightHike #MountainRace #SurvivalChallenge"],
         "tags": [SPECIFIC[13]] + TAGS},
    14: {"title": "FIVE More Hills Destroyed Their Race #shorts",
         "desc": ["Just when they thought it was over: five more hills and a storm building.",
                  "Walking blind for an hour pushes their bodies to the absolute limit - Jimmy starts throwing up.",
                  "#Shorts #DesertRace #PhysicalLimit #ExtremeChallenge"],
         "tags": [SPECIFIC[14]] + TAGS},
    15: {"title": "A 50 MPH Storm STALLED Their Final Push #shorts",
         "desc": ["Mom's send-off, one final sprint - then 50-mile-an-hour gusts blind them mid-run.",
                  "Visibility dies and they hunker down. Behind them, Thea is pushing the bag at 72%.",
                  "#Shorts #Sandstorm #FinishLine #SurvivalRace"],
         "tags": [SPECIFIC[15]] + TAGS},
}

prof = {
    "src": PROJ + r"\output\4k video\en\I Survived The Most Extreme Places On Earth [gTKS8SAwUzE].h264.mp4",
    "lang": "en",
    "plain": PROJ + r"\output\transcript\en\plain_g3.txt",
    "moments": PROJ + r"\output\temp\moments_g3.json",
    "tag": "I Survived Extreme Places v2",
    "base": PROJ + r"\output\final clips\extreme\en\I Survived Extreme Places\v2",
    "measured": {},
    "hooks": {str(k): v for k, v in hooks.items()},
    "slugs": {str(k): v for k, v in slugs.items()},
    "meta": {str(k): v for k, v in meta.items()},
}

# inputs must exist before we bless the profile
for key in ("src", "plain", "moments"):
    assert os.path.isfile(prof[key]), f"missing input: {prof[key]}"

out = os.path.join(PROJ, "system", "profiles", "g3.json")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump(prof, f, ensure_ascii=True, indent=1)
    f.write("\n")

# quick self-check (Stage-6 contract, same rules as seo_stage6.validate)
assert len(prof["hooks"]) == len(prof["slugs"]) == len(prof["meta"]) == 15
for k, h in hooks.items():
    assert len(h.split()) <= 8 and h.isupper(), (k, h)
assert len(set(hooks.values())) == 15, "hooks not unique"
assert len(set(slugs.values())) == 15, "slugs not unique"
for k, e in meta.items():
    t = e["title"]
    assert len(t) <= 100 and t.isascii(), (k, t)
    assert any(w.isupper() and len(w) > 2 for w in t.split()), (k, t)
    assert len(e["desc"]) == 3, (k, "desc lines")
    assert all(d.isascii() for d in e["desc"]), (k, "desc ascii")
    hashes = [w for w in e["desc"][2].split() if w.startswith("#")]
    assert 3 <= len(hashes) <= 5 and "#Shorts" in hashes, (k, hashes)
    assert 10 <= len(e["tags"]) <= 15 and len(", ".join(e["tags"])) <= 470, (k, "tags")
print("wrote", out)
print("hooks/slugs/meta = 15/15/15  self-check OK")
print("title lens:", sorted(len(e["title"]) for e in meta.values()))
