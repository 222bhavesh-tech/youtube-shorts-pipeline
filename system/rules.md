# Rules

## Trigger

When user types "youtube system", "make shorts", "cut viral clips", or provides a YouTube URL for Shorts:

1. Read D:\youtube system\system\SKILL.md
2. Read D:\youtube system\system\references\tool-routing.md (EXACT tools per stage)
3. Read D:\youtube system\system\references\encoding-settings.md
4. Read D:\youtube system\system\references\error-handling.md
5. Follow SKILL.md + tool-routing.md exactly
6. Respond: "Hello Sir! What would you like to do?
   1. YouTube Link — I will download and run the full pipeline
   2. Personal File — Provide video path, I will skip download"

## MCP Servers

| Server | Command | Tools |
|--------|---------|-------|
| youtube | python "D:\youtube system\system\youtube-mcp-server\server.py" | 13 (upload, A/B) |
| youtube-seo | python "D:\youtube system\system\youtube-mcp-seo\server.py" | 16 (SEO, analytics) |

All video editing = system FFmpeg (ONE pass per clip). kinocut removed from this project.

## Clip Duration (UPDATED RULE — 70s FIXED)

- **Default and target: 70 seconds. Fixed.** The QC gate accepts 65–120s only so
  legacy 75–120s videos still pass — every clip the agent cuts from now on is **70s**.
- Agent reads the transcript and extracts the BEST moments.
- Selection (Stage 3): 15 non-overlapping clips, sentence-snap window **65–75s**
  centred on the 70s target — the pick lands on the sentence closest to 70s.
- Start: natural sentence boundary (first 0.5s = hook)
- End: natural sentence boundary (no mid-word cut)
- Duration is a **variable** `$DUR` (= 70) — never hardcode 34.3s or 80s.
- NEVER exceed 120s (hard QC gate). A moment that cannot fit in 65–75s? → CUT. Split into 2 clips.

FFmpeg (variable duration, target 70, QC gate 65–120):

```
# $DUR = 70 (fixed target). QC gate: 65-120s. Max allowed: 120
ffmpeg -y -ss $START -t $DUR -i $src `
  -vf "...,fade=t=in:st=0:d=0.5,fade=t=out:st=($DUR-1.5):d=1.5" `
  -af "...,afade=t=in:st=0:d=0.5,afade=t=out:st=($DUR-1):d=1,loudnorm=I=-14" `
  ...
```

Examples: every clip = 70s.

## Fades (UPDATED)

Video (in the ONE -vf chain):
```
fade=t=in:st=0:d=0.5,fade=t=out:st=($DUR-1.5):d=1.5
```

Audio (in the ONE -af chain):
```
afade=t=in:st=0:d=0.5,afade=t=out:st=($DUR-1):d=1
```

Never hardcode $DUR — always expression form. Fade-out completes exactly at clip end.

## Captions Rule
- Captions, hook title, and metadata are ALWAYS in English (caption font: Montserrat Bold 96px — never Mangal) — regardless of audio language.
- Only the AUDIO track changes per channel (EN audio / HI audio).
- Do NOT translate captions. Do NOT use Mangal. Do NOT generate Hindi ASS.

## Overlays — NONE (CTA REMOVED)

NO overlays of any kind — EXCEPT the "Top Overlay Timeline" below (the only overlays this project allows). NO CTA. The only visuals in a clip are: hook pill + hook title (t 1–15, with fades), like-comment-subscribe (t 25–30, auto-removed), center-subscribe popup (t 60→end, centered in the MAIN band, removed by the global end fade), captions, and fades.
- **Notification Bell and YouTube Subscribe are REMOVED permanently (user 2026-09-26)** — they froze in place to clip end instead of exiting smoothly. Never re-add them.
- No speed lines, no confetti, no arrows, no hearts, no particles, no glitch, no emoji, no kinetic text, no transitions, no extra CTAs.
- Old CTA assets deleted from the project (`system\assets\overlays\cta\` removed). Never re-add or re-introduce anything outside the timeline.

## Critical Rules

- NEVER upload. EVER. Show all clips to user (file paths) and wait for the explicit "Upload" or "pass" command. No exceptions.
- ALWAYS run MCP health check before starting (youtube + youtube-seo)
- ALWAYS ONE ffmpeg pass per clip with the Mode from the SKILL.md content table (Mode B blurred bg = default · Mode A face-track = podcast · center-crop = movies/gaming) (kinocut removed — never call it)
- ALWAYS verify output with ffprobe (1080x1920, h264, 65-120s target 70, aac) before showing or uploading
- Outputs ONLY under `output\final clips\<category>\<lang>\<video>\`; inputs stay at `output\` root in per-language subfolders (`4k video\en|hi\`, `transcript\en|hi\`, `face_track\en|hi\`)
- No generated images / thumbnails — upload without thumbnail_path (youtube_set_thumbnail + youtube_ab_start ONLY if user asks)
- If any MCP is disconnected: STOP and tell user
- If source has no SRT: FunClip backup runs automatically — agent-only, never ask user (see FunClip section)
- Progress report after every stage
- Keep D:\youtube system\ clean (no stray files, no empty folders)

## FunClip (BACKEND ONLY — NO GUI, NO BROWSER, NO USER ACTION)

- FunClip is controlled 100% by agent via gradio_client API.
- Agent starts server: run_funclip_headless.bat (background, no browser window)
- Agent calls: gradio_client → http://localhost:7860/ → `/mix_recog` (FunClip has NO `/transcribe` endpoint — verified live)
- Agent saves SRT to: output\transcript\en\[Title].en.srt
- Agent continues pipeline automatically.
- User does NOTHING. No browser. No GUI. No manual click.
- If FunClip not running: agent starts it. User doesn't know it happened.
- If FunClip crashes: agent restarts it. User doesn't know.
- This is BACKEND. Not a tool the user opens. Not a website. Invisible to user.

## Top Overlay Timeline (70s, STACKED, PERMANENT)

Overlays **stack** — each one enters at its start time and STAYS until the end of
the clip. They never replace each other. The video plays normally underneath;
overlays are burned in (no added duration).

| Enters | Overlay | File | Window | Exit |
|--------|---------|------|--------|------|
| 1s | Hook title (pill + drawtext) | hook_pill.png | 1–15s | fade in 0.5s @1, fade out 0.5s @14.5, then removed |
| 25s | Like + Comment + Subscribe | like-comment-subscribe.mp4 | 25–30s | full 5s asset plays (LIKE→COMMENT→SUBSCRIBE + collapse-outro ends empty) → auto-removed, NO freeze |
| 60s | Center Subscribe (popup) | center-subscribe.mov | 60–69.4s | bounce pop-in 60→60.3, hold, bounce-out 69→69.3 (content gone), empty after; global end fade covers clip end |

- REMOVED permanently (user 2026-09-26): Notification Bell (was 40s→end) and
  YouTube Subscribe (was 60s→end) — they froze in place instead of exiting
  smoothly. Never re-add.
- Hook: `x=0, y=84` (top blur zone) — alone 1–15s, nothing else coexists with it.
- Like + Comment + Subscribe: `x=268, y=56` (top-blur zone, CENTERED — its
  544×107 content lands on (540,192), the middle of the 0–384 zone; user
  2026-09-28 corrected the old y=179 bottom-center placement).
- Center Subscribe: the ONLY main-band overlay — full 4K frame scaled to
  991 wide (+20% per user 2026-09-29; was 826) → 991×558 canvas at
  `x=44.5, y=534.6`; the loop-held f296 content is 614×172 (content-center
  offset (497.7, 281.4) → pins to main-band center x=540 y=816 — verified
  on a rendered frame: red bbox 724×200 incl. bleed, center (539,815); the
  relayed y=691 assumed a 250px-tall asset and would sit 109px low).
  Bounce in 60→60.3, hold, bounce out 69→69.3 →
  gone; `enable='between(t,60,69.4)'` closes the window (29.97 src vs
  30fps asset clock drift), then empty — NO more hold-to-end (the global
  end fade, last 1.5s, still covers clip end).
- Clean windows: 15–25s, 30–60s, 69.4s→end (video + captions only).
- Never in subtitle zone. Never added duration — overlays burn into the playing video.
- This timeline is FIXED.

## Overlay Animation
- Animated overlays END ON AN EMPTY/TRANSPARENT FRAME — hold the last
  VISIBLE frame, never the true EOF. Center-subscribe: every frame in the
  window IS loop-held f296 (f296 = last visible frame of the 300f asset;
  `loop=loop=-1:size=1:start=296` drops the empty f297-299 tail and
  repeats f296 — verified gap-free) with a per-frame K-scale doing the
  bounce. like-comment-subscribe does NOT hold at all: its full 5s plays
  (25→30) and its collapse-outro ends empty → auto-removed.
- notification-bell / youtube-subscribe: REMOVED permanently (2026-09-26) —
  their freeze-held frames sat on screen to clip end; never re-add.
- Hook: pill input `-framerate 30 -loop 1 -t $DUR -i hook_pill.png`, drawtext centered
  ON the pill (`x='(W-text_w)/2':y='(H-text_h)/2'`), `fade=t=in:st=1:d=0.5:alpha=1,
  fade=t=out:st=14.5:d=0.5:alpha=1` + `enable='between(t,1,15)'`.
- Center-subscribe: `format=rgba,scale=991:-2,loop=loop=-1:size=1:start=296,
  scale=w='max(2,991*K)':h=-2:eval=frame` with
  `K=min(min(max((t-60)/0.3,0),1),1-min(max((t-69)/0.3,0),1))`,
  overlay `x='44.5+495.5*(1-K)':y='534.6+279*(1-K)':enable='between(t,60,69.4)'`
  — K drives the bounce (in 60→60.3, out 69→69.3) and the x/y re-anchor
  so it pops about its content center. TRAPS (all tested on the WinGet
  7.1.1 build): scale defaults to eval=init and REJECTS t-exprs →
  eval=frame is mandatory; w=0 means "input width" (would flash the full
  4K canvas) → clamp ≥2; NO setpts+60 — loop keeps pts on the clip
  timeline so scale's t and enable's t share one clock (overlay pairs
  inputs BY PTS).
- LCS: instant on via `enable='gte(t,25)'` — no added fade/scale/opacity;
  the file's own built-in animation is the only look. It plays its full
  5s (25→30) and auto-removes when the file ends — NEVER freeze-hold
  (the old trim@4.0+tpad froze SUBSCRIBE to clip end; user removed it).
- Overlay audio is NEVER mapped.
- Output MUST be bounded with `-t $DUR` — the CS loop-hold makes that
  input infinite; without `-t` the encode never ends.

## Do NOT trigger for

- Single clip editing (not batch Shorts)
- Long-form video editing (> 3 min)
- Audio-only work (podcast, music)
- AI video generation
- Non-YouTube platforms
