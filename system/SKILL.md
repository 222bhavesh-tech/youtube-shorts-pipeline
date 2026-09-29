---
name: youtube-shorts-pipeline
description: |
  Full YouTube Shorts automation: download, transcribe, cut viral moments,
  encode with animated captions in ONE ffmpeg pass (Mode A/B per content type),
  SEO optimize, and upload only after explicit user "pass". Use when user says
  "youtube system", "make shorts", "cut viral clips", or provides a YouTube URL.
when_to_use: |
  Trigger phrases: "youtube system", "make shorts from", "cut this video into shorts",
  "create shorts", "viral clips from", "youtube shorts pipeline"
  Also trigger when: user provides a YouTube URL and mentions "shorts" or "clips"
  Do NOT trigger for: long-form editing, podcast editing, live stream clipping
compatibility: |
  Requires: Python 3.12+, FFmpeg 9.0.1 + yt-dlp on PATH, 2 MCP servers
  (youtube, youtube-seo), MediaPipe (Mode A). Windows.
  NOTE: kinocut is REMOVED from this project — ALL video work = ONE ffmpeg pass.
metadata:
  version: "2.1.0"
  author: "bhavesh"
  platform: "windows"
---

# YouTube Shorts Pipeline

## ⚠️ FORMAT REQUIREMENT
- **ALL output clips MUST be 9:16 vertical (1080x1920)** — NON-NEGOTIABLE
- How you get to 9:16 depends on content type → Mode table in Stage 4

---

## The 8 Components

| # | Component | Role | Location | Verified |
|---|-----------|------|----------|----------|
| 1 | FFmpeg 9.0.1 | ALL video work (1 command) | `D:\FunClip\tools\ffmpeg\bin\` (= PATH) | ✓ |
| 2 | MediaPipe | Face track (Mode A, single-person) | pip (1.0.1) | ✓ |
| 3 | FunClip | Backup transcription (no SRT) | `D:\FunClip\` | ✓ |
| 4 | yt-dlp | Download video + SRT | pip | ✓ |
| 5 | ffprobe | Probe + QC | with FFmpeg | ✓ |
| 6 | OpenCode LLM | Brain (pick moments, write metadata, decide Mode A/B) | Built-in | ✓ |
| 7 | YouTube MCP | Upload + SEO audit | `D:\youtube system\system\youtube-mcp-server\` | ✓ |
| 8 | YouTube-SEO MCP | Score + analytics | `D:\youtube system\system\youtube-mcp-seo\` | ✓ |

Fonts (loaded via `fontsdir`/`fontfile`, NOT system-installed): Montserrat Bold (captions 96px + hook banner 40px) → `D:\youtube system\output\temp\fonts\` (Anton-Regular.ttf present but retired for captions)

---

## Step 0: Verify MCPs (ALWAYS FIRST)

Before starting, verify both MCP servers:
- **youtube**: `youtube_whoami()`
- **youtube-seo**: `get_channel_overview()`

If ANY fails → tell user which one → DO NOT proceed.

---

## Pre-flight Checks (before Step 1)

- [ ] FFmpeg on PATH: `ffmpeg -version` (must resolve to `D:\FunClip\tools\ffmpeg\bin\ffmpeg.exe`, 9.0.1)
- [ ] yt-dlp installed: `yt-dlp --version`
- [ ] MediaPipe available: `python -c "import mediapipe"` (only needed for Mode A)
- [ ] `D:\youtube system\` exists and writable
- [ ] Free disk space > 5 GB: `(Get-PSDrive D).Free / 1GB`
- [ ] Both MCPs connected (Step 0)

If ANY check fails → stop and tell user what's missing.

---

## Stage 1: Download + Subtitles

```
yt-dlp → save to D:\youtube system\output\4k video\en\ (HI: 4k video\hi\ — `-f "bv*+ba[language=en]"` / `[language=hi]`)
yt-dlp --write-subs --sub-lang en --convert-subs srt --skip-download → save to D:\youtube system\output\transcript\en\ (HI SRT → transcript\hi\)
Convert VTT → SRT → plain.txt → transcript\en\plain.txt (captions ALWAYS read transcript\en\)
```

**Errors:**
- Video unavailable/region locked → tell user, ask for manual download path
- No SRT found → ask: "Use FunClip to transcribe? (~5 min)"

---

## Stage 2: Analyze Source (system CLIs — no MCP)

```
ffprobe            → resolution, codec, fps, duration
ffmpeg scene       → select='gt(scene,0.3)' → cut boundaries
ffmpeg silence     → silencedetect -30dB → silence gaps
```

**Errors:**
- Video < 5 min → reduce to 3-5 clips of 70s, tell user
- Video > 1 hour → cap at 20 clips, tell user

---

## Stage 3: Select 16 Viral Moments

From transcript + scene analysis, pick clips:
- Hook (first 3-5s must grab)
- Emotional peaks (arguments, surprises, failures)
- Pattern interrupts
- Satisfying moments (results, reveals)
- Cliffhangers

**Default clip timestamps (seconds):**
1. The Hook (0-75)
2. First Night Fail (81-140)
3. Red Team Living Large (146-180)
4. Expert Shelter (174-210)
5. Amateurs Waste Resources (220-280)
6. Food Drop Chaos (600-660)
7. 50 Can Challenge (680-740)
8. Can Results Shock (910-970)
9. Storm Hits (1290-1370)
10. Tent Destroyed (1370-1440)
11. Frost Morning (1530-1600)
12. Box Challenge (1680-1770)
13. Blue Gets Steaks (1770-1830)
14. Tarp Drama (1850-1920)
15. Girl Leaves in Tears (2000-2060)
16. Winner Revealed (2100-2200)

---

## Stage 4: Encode — ONE ffmpeg pass per clip (pick Mode first)

**Mode selection (per VIDEO content type):**

| Content type | Mode | Technique |
|--------------|------|-----------|
| MrBeast / Extreme / Action | **Mode B (default)** | 3-zone blurred bg: fg fill-crop 1080×864 hero band over gblur'd darkened fill |
| Vlog / Travel | Mode B | Blurred bg |
| Podcast / Interview (single person) | Mode A | MediaPipe face-track crop + silenceremove in -af |
| Movies (extract clips) | Center-crop | `crop=ih*9/16` formula (auto-adjusts) |
| Gaming / Screen | Center-crop | Fixed center crop |
| Multi-language (Hindi/ES) | Any mode | Same English ASS both channels — only `-i` source changes (`4k video\en` vs `4k video\hi`). Captions always English Montserrat Bold (Captions Rule) |

**The ONE command** (all modes share it — only the video filter part changes):

- `-ss START -t 70 -i SRC` (SRC single-quoted — filenames contain `$`)
- **Mode B video chain**: `split` → [bg] `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.25` + [fg] `scale=1080:864:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:864` → `overlay=0:384` (zones 20/45/35: top blur 384 / hero band 864 / bottom blur 672)
- **Mode A video chain**: `crop=608:1080:'<MEDIAPIPE_EXPRESSION>':0,scale=1080:1920:flags=lanczos` (4K source → `scale=1920:1080` first; expression from INLINE MediaPipe `python -c` — NO separate face_track.py file)
- **Center-crop video chain**: `crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920:flags=lanczos`
- then ALWAYS: `ass='NN.ass':fontsdir='fonts'` (Montserrat Bold 96px mixed case — per-line `\an8\pos+\fsp-0.5`, ACTIVE_RISE pop comp; active word #FFE500 +10% pop, inactive #FFFFFF, outline 4 / shadow 3; caption-styles.md v2.3) → Top Overlay Timeline STACKED (rules.md): hook pill `overlay=0:84:enable='between(t,1,15)'` + Montserrat Bold 40px drawtext centered on the pill (t=1–15, 0.5s fade in/out) → like-comment-subscribe `gte(t,25)` (x=268 y=56) → center-subscribe `between(t,60,69.4)` (MAIN band x=44.5 y=534.6 re-anchored by K, frame scaled to 991 wide = +20% per user 2026-09-29, K-bounce in 60→60.3 / out 69→69.3, loop-held f296, gone after 69.3; global end fade covers clip end) — LCS plays its full 5s 25→30 then auto-removes (NO freeze) (notification-bell + youtube-subscribe REMOVED permanently 2026-09-26 — they froze to clip end; never re-add) → NO CTA (rules.md "Overlays — NONE (CTA REMOVED)") → fades (rules.md Fades UPDATED): in 0.5s video+audio, out video 1.5s (st=$DUR-1.5) / audio 1s (st=$DUR-1) → output bounded `-t $DUR` (CS loop-hold is infinite)
- audio: `[0:a]` afade 0.5s in/out → `loudnorm=I=-14:TP=-1:LRA=11` (PODCAST: prepend `silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.5,`)
- export: libx264 CRF 18 ultrafast, AAC 192k 48kHz, +faststart, yuv420p

**Exact command:** `references/tool-routing.md` → Stage 4. Run from `D:\youtube system\output\temp` (drive-colon paths break ffmpeg's filter parser — relative paths inside filters only).

**Errors:**
- ffmpeg filter path error (`No option name near 'D:'`) → cd to temp\, relative paths in filters
- ffmpeg exits 1 but output exists → SUCCESS (verify with ffprobe, never with exit code)
- Montserrat missing at `C:\Windows\Fonts` → use `fonts/montserrat-bold.ttf` relative (fonts live in temp\fonts)
- Mode A expression drift → recompute MediaPipe on same resolution as crop input
- kinocut tool fails → N/A: kinocut is REMOVED from this project, never call it

---

## Crop Logic (Mode: center-crop — movies/gaming)

After `ffprobe`, determine source aspect ratio:

| Source | Crop formula |
|--------|-------------|
| 16:9 (3840x2160, 1920x1080, 2560x1440) | `crop=ih*9/16:ih:(iw-ih*9/16)/2:0` |
| 9:16 (already vertical) | No crop. Just `scale=1080:1920:flags=lanczos` |
| 1:1 (square) | `crop=ih:ih:0:0` + `pad=1080:1920:(1080-ih)/2:0:color=black` |
| 4:3 | `crop=ih*9/16:ih:(iw-ih*9/16)/2:0` |

**NEVER hardcode pixel crop values. Always calculate from actual resolution.**

---

## Caption Font

- Captions (English / Latin-script Hinglish): **Montserrat Bold 96px** — caption-styles.md v2.3 spec (mixed case, per-line `\an8\pos(540,y)\fsp-0.5`, pitch 71.5 / last ink top 1464 / ACTIVE_RISE 6.82, active #FFE500 +10% pop / inactive #FFFFFF, outline 4 / shadow 3, 3 lines max)
- Hook banner: pill PNG `assets\hook_pill.png` (1080×120, r50, α235) at `overlay=0:84` + **Montserrat Bold** 40px black centered on the pill canvas — title UNIQUE per clip (prompt.md Hook Title Rule), t=1–15 with 0.5s fade in/out (rules.md timeline)
- Overlays: only the Top Overlay Timeline (rules.md) — no CTA, no other animations/effects ever. Inputs are exactly 4: source + hook_pill.png + like-comment-subscribe.mp4 + center-subscribe.mov. notification-bell.mov + youtube-subscribe.mp4 are REMOVED permanently (2026-09-26) — never re-add.
- Devanagari/Hindi content: captions stay **English + Montserrat Bold** (Captions Rule) — audio track changes per channel, captions never translate, never Mangal
- Font files: `D:\youtube system\output\temp\fonts\` passed via `fontsdir=fonts` / `fontfile='fonts/...'`
- ASS generation: `system\gen_ass.py` → `ass\NN.ass`

---

## Stage 5: QC Gate (ffprobe)

```
Verify per clip: 1080x1920 · h264 · 65-120s (target 70s) · aac audio present · file exists · size > 50MB
FAIL → re-run Stage 4 once → re-verify
Still FAIL → skip clip, tell user. Never show/upload broken video.
```

---

## Stage 6: SEO + Upload

Generate:
- Title (100 chars max, keyword-rich)
- Description (first 2 lines crucial) + #Shorts + 3-5 hashtags
- Tags (10-15 keywords)

Pre-upload SEO = manual checklist (`get_video_seo_score` only accepts an uploaded `video_id`). Score < 70 → revise, max 2 cycles.

**Errors:**
- SEO score < 50 → flag it, suggest manual review
- YouTube upload fails (quota) → tell user, save to upload_sheet.txt

---

## Upload (REQUIRES USER CONFIRMATION)

Before uploading ANY clip:
1. Show full list: Clip # | Title | Duration | SEO Score
2. Wait for the user's explicit command: `pass` / `pass 01 03` / `redo 02` / `skip 05` / `stop`
3. Upload ONLY on `pass` (or specific clip numbers after `pass`)
4. After upload, show confirmation with video URLs

**NEVER upload without explicit user "pass"/"upload" command. No exceptions.**

---

## Progress Reporting

After each major stage, report:

```
[1/9] Download... ✅ (2:34 min, 1.64 GB)
[2/9] Analyze... ✅ (12 scene boundaries found)
[3/9] Select clips... ✅ (16 clips chosen, 70s each)
[4/9] Encode clip 01/16... ✅ (45 MB)
[4/9] Encode clip 02/16... ✅ (52 MB)
...
[9/9] Upload... ✅ (16/16 uploaded)
```

If a step fails:
```
[4/9] Encode clip 07/16... ❌ FAILED (reason: ...)
       → Retrying... ✅
```

---

## Error Handling

| Error | Fallback |
|-------|----------|
| yt-dlp fails (video unavailable) | Tell user, ask for manual download path |
| No SRT found | Ask: "Use FunClip to transcribe? (~5 min)" |
| Source not 16:9 | Use dynamic crop formula (or Mode B blur for any ratio) |
| Video < 5 min | Reduce to 3-5 clips of 70s |
| Video > 1 hour | Cap at 20 clips |
| ffmpeg filter path error | cd to temp\, relative paths inside -vf/-af |
| ffmpeg exits 1, output exists | Success — verify with ffprobe |
| Mode A face-track drift | Recompute MediaPipe at crop-input resolution |
| Encode fails mid-clip | Shift START, retry once, then skip clip |
| YouTube upload fails (quota) | Tell user, save to upload_sheet.txt |
| SEO score < 50 | Flag it, suggest manual review |
| FFmpeg not found | Tell user: "FFmpeg lives at D:\FunClip\tools\ffmpeg\bin\" |
| Disk space < 5GB free | Tell user: "Need 5GB free space" |

---

## Do NOT Use This Skill When:

- User wants to edit a single clip (not batch Shorts)
- User wants long-form video editing (> 3 min output)
- User wants to edit audio only (podcast, music)
- User wants to create AI-generated video (not editing existing)
- User wants to upload to platforms other than YouTube
- User just wants transcription without video editing

---

## The Toolset (kinocut REMOVED — all video work = FFmpeg 9.0.1)

| # | Tool | Stage | Purpose |
|---|------|-------|---------|
| 1 | yt-dlp | 1 | Download 4K video + SRT |
| 2 | ffprobe | 2, 5 | Source probe + QC verify |
| 3 | ffmpeg (scene/silence detect) | 2 | Cut boundaries |
| 4 | gen_ass.py | 4 | Generate per-clip ASS captions |
| 5 | ffmpeg (ONE encode pass) | 4 | Mode A/B/crop → composite → captions → hook → loudnorm → export |
| 6 | MediaPipe (inline python -c) | 4A | Face-track crop expression (Mode A, single-person) |
| 7 | youtube_whoami | 0 | MCP health check |
| 8 | get_channel_overview | 0 | MCP health check |
| 9 | youtube_upload | 6 | Upload (only after user "pass"; no thumbnail) |
| 10 | youtube_seo_audit | 6 | Post-upload audit |
| 11 | get_video_seo_score | 6 | Real score (needs video_id) |
| 12 | get_video_details | 6 | Pull uploaded metadata |
| 13 | FunClip | 1 | Transcription backup (only if no SRT) |

Not used by this pipeline: `youtube_set_thumbnail`, `youtube_ab_start` (thumbnail pipeline removed — uploads ship without a custom thumbnail; only call if the user explicitly asks).

---

## Output Format
- **Aspect Ratio**: 9:16 (1080x1920) — ALL clips
- **Resolution**: 1080x1920
- **Audio**: AAC 192kbps stereo, 48kHz
- **Video**: H.264, CRF 18, ultrafast preset
- **Duration**: 70s per clip (fixed; QC gate 65-120s so legacy videos still pass)

## Quality Rules
- Never use CRF > 20 for final output
- Always verify 9:16 before export (Mode A/B/crop — but 9:16 always)
- No blurry frames (except intentional gblur background)
- Audio must be normalized to -14 LUFS
- Subtitles must be readable on mobile
- ffmpeg exit code never decides success — ffprobe does
- Exactly ONE re-encode per clip — chain nothing

## File Organization
```
D:\youtube system\
├── output\
│   ├── 4k video\        # Source videos, per language: en\ hi\ (inputs)
│   ├── transcript\      # SRT files, per language: en\ hi\ — captions always read en\ (inputs)
│   ├── face_track\      # Crop expressions + track JSON per language: en\ hi\, prefixed per video
│   ├── temp\            # Working dir for ffmpeg (run here!) + fonts\
│   └── final clips\     # Outputs ONLY
│       └── [category]\[lang]\[Video Title]\   # e.g. extreme\en\I Stranded 100 People\
│           ├── ass\     # Per-clip ASS caption files
│           ├── clips\   # Final encoded MP4s
│           ├── metadata\# NN.txt title/desc/tags
│           └── upload_sheet.txt
└── system\
    ├── references\      # tool-routing, encoding, captions, errors
    └── SKILL.md         # This file
```
Category = extreme | funny | podcast | kids | movies | facts | motivation · lang = en | hi
