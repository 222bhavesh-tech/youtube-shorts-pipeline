# Stage 6: write metadata\NN.txt per clip (title / description / tags).
import os, sys
import src_profile
PROF, _ = src_profile.load(sys.argv[1:])

OUT = os.path.join(PROF["base"], "metadata")
os.makedirs(OUT, exist_ok=True)

M = {
1: {
 "title": "He Gets $10,000 EVERY DAY Trapped In A Grocery Store #shorts",
 "desc": [
  "He gets $10,000 every single day \u2014 as long as he never leaves the grocery store.",
  "One guy, one store full of food, one red line. Crossing it ends everything. How long can he stay?",
  "#Shorts #GroceryStoreChallenge #ExtremeChallenge #10000Dollars #Survival",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "10000 dollars a day",
          "survive in grocery store", "extreme challenge", "money challenge",
          "mrbeast style", "youtube shorts", "10k challenge", "grocery store",
          "survival challenge"],
},
2: {
 "title": "Selling $10,000 Of DOG FOOD To Survive The Grocery Store #shorts",
 "desc": [
  "Selling $10,000 of dog food and TVs just to earn another day inside.",
  "Every day he must hand over $10,000 in products to keep the cash coming \u2014 the strategy starts now.",
  "#Shorts #GroceryStoreChallenge #MoneyChallenge #MrBeastStyle #Survival",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "dog food challenge",
          "10000 dollars a day", "money challenge", "selling for survival",
          "mrbeast style", "youtube shorts", "extreme challenge", "strategy",
          "electronics haul"],
},
3: {
 "title": "The Produce Will GO BAD Fast... 100 Days Inside #shorts",
 "desc": [
  "The produce will go bad fast \u2014 and he just cleared $30,000 worth of product.",
  "Day 10 inside the store: a makeshift shower, $100K in the bank, and a goal of 100 days.",
  "#Shorts #GroceryStoreChallenge #ExtremeChallenge #Survival #10KADay",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "100 days challenge",
          "produce challenge", "survival challenge", "10000 dollars a day",
          "makeshift shower", "mrbeast style", "youtube shorts", "extreme challenge",
          "longest challenge"],
},
4: {
 "title": "He Built A CHEESE BALL Wall Inside A Grocery Store #shorts",
 "desc": [
  "He built a wall out of cheese balls while living inside a grocery store.",
  "$100,000 delivered by \u201CThe Money Man\u201D \u2014 and a functioning shower made from raw store parts.",
  "#Shorts #GroceryStoreChallenge #CheeseBallWall #MrBeastStyle #Extreme",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "cheese ball wall",
          "living in grocery store", "money man", "shower build", "mrbeast style",
          "youtube shorts", "extreme challenge", "10000 dollars a day", "funny challenge"],
},
5: {
 "title": "He Built A Bed From TOILET PAPER In A Grocery Store #shorts",
 "desc": [
  "A bed made of toilet paper and walls built from water bottles.",
  "He hit $10,000 using only birthday cards \u2014 then Jimmy brought him a forklift.",
  "#Shorts #GroceryStoreChallenge #Creative #Survival #MoneyChallenge",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "toilet paper bed",
          "birthday cards challenge", "forklift", "living in grocery store",
          "mrbeast style", "youtube shorts", "extreme challenge", "10000 dollars a day",
          "creative survival"],
},
6: {
 "title": "$10,000 Of GOLDFISH?! Scanning Another Day Inside #shorts",
 "desc": [
  "$10,000 worth of goldfish \u2014 and a million-dollar goal that\u2019s starting to crack.",
  "Day 22 inside the store: new forklift, upgraded bed, and a hard choice about his family.",
  "#Shorts #GroceryStoreChallenge #Goldfish #10KADay #ShortsViral",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "goldfish",
          "10000 dollars a day", "million dollars challenge", "forklift",
          "mrbeast style", "youtube shorts", "extreme challenge", "scanning items",
          "family decision"],
},
7: {
 "title": "30 Days In: His Family SURPRISED Him At The Store #shorts",
 "desc": [
  "The days started blending together \u2014 then his family walked in.",
  "30 days of isolation rewarded with the surprise of his life. But the power is getting cut off next.",
  "#Shorts #GroceryStoreChallenge #FamilySurprise #Emotional #MrBeastStyle",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "family surprise",
          "30 days in grocery store", "emotional reunion", "power outage",
          "mrbeast style", "youtube shorts", "extreme challenge", "isolation challenge",
          "kids surprise"],
},
8: {
 "title": "I Made A RACE CAR Track Inside A Grocery Store #shorts",
 "desc": [
  "He made a race car track inside the grocery store \u2014 then the lights went out.",
  "A final day with his kids, and then Jimmy pulls the plug on the store\u2019s electricity.",
  "#Shorts #GroceryStoreChallenge #RaceCarTrack #PowerOutage #Extreme",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "race car track",
          "power outage challenge", "living in grocery store", "family visit",
          "mrbeast style", "youtube shorts", "extreme challenge", "electricity cut",
          "toy car track"],
},
9: {
 "title": "Power Cut Off! Selling FROZEN Food In The Dark #shorts",
 "desc": [
  "Power is out \u2014 now he is selling frozen food in the dark.",
  "Cash registers on a generator, meat on clearance, and $60,000 waiting. Day 36 gets brutal.",
  "#Shorts #GroceryStoreChallenge #PowerOutage #Survival #10KADay",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "power outage",
          "selling frozen food", "dark challenge", "generator only", "10000 dollars a day",
          "mrbeast style", "youtube shorts", "extreme challenge", "survival challenge"],
},
10: {
 "title": "He Found $360,000 In CASH Inside A Grocery Store #shorts",
 "desc": [
  "$360,000 in cash \u2014 and the red line has never been more tempting.",
  "Pools of money, no power, nothing to do. Lanterns light up his darkest days inside the store.",
  "#Shorts #GroceryStoreChallenge #CashMoney #360K #ExtremeChallenge",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "360000 dollars",
          "cash money", "red line temptation", "lantern light", "money pool",
          "mrbeast style", "youtube shorts", "extreme challenge", "10000 dollars a day"],
},
11: {
 "title": "He Built A Swimming POOL Inside The Grocery Store #shorts",
 "desc": [
  "Lights are back, shelves are cleared \u2014 and he built a swimming pool.",
  "Jimmy returns after a week to find the store completely remodeled. Time to cannonball.",
  "#Shorts #GroceryStoreChallenge #SwimmingPool #Forklift #ViralShorts",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "grocery store pool",
          "forklift remodeling", "swimming pool challenge", "lights back on",
          "mrbeast style", "youtube shorts", "extreme challenge", "living in grocery store",
          "cannonball"],
},
12: {
 "title": "It's FREEZING! He Flooded The Store With The Forklift #shorts",
 "desc": [
  "It\u2019s freezing \u2026 cannonball! Then the forklift went the wrong way.",
  "One bad turn flooded the entire store. Products ruined, pool busted \u2014 and Alex wanted out.",
  "#Shorts #GroceryStoreChallenge #ForkliftFail #Flooded #OhNo",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "forklift crash",
          "flooded store", "pool disaster", "funny fail", "mrbeast style",
          "youtube shorts", "extreme challenge", "warehouse fail", "10000 dollars a day"],
},
13: {
 "title": "How Does One BUST A POOL In A Grocery Store?! #shorts",
 "desc": [
  "How does one bust a pool inside a grocery store?",
  "The store before vs. after 44 days \u2014 and day 44 starts with no $10,000 delivery at all.",
  "#Shorts #GroceryStoreChallenge #PoolDisaster #BeforeAndAfter #Extreme",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "busted pool",
          "before and after", "44 days challenge", "lonely challenge",
          "mrbeast style", "youtube shorts", "extreme challenge", "10000 dollars a day",
          "warehouse disaster"],
},
14: {
 "title": "ARE YOU THERE JIMMY?! 45 Days Alone In The Dark #shorts",
 "desc": [
  "\u201CAre you there, Jimmy?\u201D \u2014 day 45 of complete isolation.",
  "$450,000 won, but the boredom is crushing. He can leave whenever he wants \u2026 so why doesn\u2019t he?",
  "#Shorts #GroceryStoreChallenge #Isolation #45Days #Emotional",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "isolation challenge",
          "45 days alone", "boredom", "450000 dollars", "mrbeast style",
          "youtube shorts", "extreme challenge", "missing family", "dark store"],
},
15: {
 "title": "$450,000 SEA OF MONEY - The Final Decision #shorts",
 "desc": [
  "His $450,000 sea of money \u2014 and the final decision.",
  "His family arrives with one question: is it worth it? 45 days, $450,000, one step across the red line.",
  "#Shorts #GroceryStoreChallenge #450K #FinalDecision #MrBeastStyle",
 ],
 "tags": ["shorts", "viral shorts", "grocery store challenge", "450000 dollars",
          "sea of money", "final decision", "leaving the challenge", "family verdict",
          "mrbeast style", "youtube shorts", "extreme challenge", "45 days challenge",
          "red line"],
},
}

if PROF.get("meta"):
    M = PROF["meta"]   # profile-authored metadata overrides legacy grocery

fails = []
for nn, m in M.items():
    t, d, g = m["title"], m["desc"], m["tags"]
    if len(t) > 100:
        fails.append(f"{nn:02d} title {len(t)} chars >100")
    if not t.isascii():
        fails.append(f"{nn:02d} title non-ascii")
    words = t.split()
    if not any(w.isupper() and len(w) > 2 for w in words):
        fails.append(f"{nn:02d} title no ALL CAPS hook word")
    if not (3 <= len(d) <= 3):
        fails.append(f"{nn:02d} desc lines={len(d)}")
    if "#Shorts" not in d[2]:
        fails.append(f"{nn:02d} desc missing #Shorts")
    if not (3 <= len([h for h in d[2].split() if h.startswith('#')]) <= 5):
        fails.append(f"{nn:02d} hashtags={len([h for h in d[2].split() if h.startswith('#')])}")
    if not (10 <= len(g) <= 15):
        fails.append(f"{nn:02d} tags={len(g)}")
    if len(", ".join(g)) > 470:
        fails.append(f"{nn:02d} tag block {len(', '.join(g))} chars >470")

if fails:
    print("VALIDATION FAIL:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)

for nn, m in M.items():
    path = os.path.join(OUT, f"{nn:02d}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("Title:\n")
        f.write(m["title"] + "\n\n")
        f.write("Description:\n")
        f.write("\n".join(m["desc"]) + "\n\n")
        f.write("Tags:\n")
        f.write(", ".join(m["tags"]) + "\n")

print(f"metadata written: {len(M)} files -> {OUT}")
for nn, m in M.items():
    print(f"{nn:02d} [{len(m['title']):3d}] {m['title']}")
