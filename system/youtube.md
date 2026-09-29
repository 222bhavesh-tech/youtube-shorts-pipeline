# YouTube Shorts Pipeline — Final Reference

## Architecture

┌─────────────────────────────────────────────────────────┐
│  YOU: Paste 1 YouTube URL                               │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  OpenCode (LLM Brain)                                   │
│  • Reads transcript                                     │
│  • Picks 15-18 viral moments                            │
│  • Writes titles, descriptions, tags                    │
│  • Decides Mode A / Mode B / center-crop                │
│  • Runs exact ffmpeg commands from tool-routing.md      │
└──────┬──────────────────┬──────────────────┬────────────┘
       ▼                  ▼                  ▼
┌─────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   yt-dlp    │  │  FFmpeg 9.0.1    │  │  YouTube MCP     │
│  (download) │  │  (ALL edits,     │  │  (13 tools)      │
│             │  │   1 pass/clip)   │  │                  │
└─────────────┘  └──────────────────┘  └──────────────────┘
                                  ┌──────────────────┐
                                  │  YouTube-SEO MCP │
                                  │  (16 tools)      │
                                  └──────────────────┘

kinocut: REMOVED from this project — FFmpeg 1 command = same result, 5x faster.

## The 8 Components

| # | Component | Role | Location |
|---|-----------|------|----------|
| 1 | FFmpeg 9.0.1 | ALL video work (1 command) | D:\FunClip\tools\ffmpeg\bin\ (= PATH) |
| 2 | MediaPipe | Face track (Mode A, single-person) | pip (1.0.1) |
| 3 | FunClip | Backup transcription (no SRT) | D:\FunClip\ |
| 4 | yt-dlp | Download video + SRT | pip |
| 5 | ffprobe | Probe + QC | with FFmpeg |
| 6 | OpenCode LLM | Brain (pick moments, metadata, decide Mode A/B) | Built-in |
| 7 | YouTube MCP | Upload + SEO audit | D:\youtube system\system\youtube-mcp-server\ |
| 8 | YouTube-SEO MCP | Score + analytics | D:\youtube system\system\youtube-mcp-seo\ |

Fonts (NOT system-installed): Montserrat Bold (captions 96px + hook banner 40px) → D:\youtube system\output\temp\fonts\ (Anton retired for captions)

## Folder Structure

D:\youtube system\
├── output\
│   ├── 4k video\              ← Source (yt-dlp downloads), per language: en\ hi\
│   ├── transcript\            ← SRT files, per language: en\ hi\ — captions always read en\
│   ├── face_track\            ← Crop expressions, per language: en\ hi\, prefixed per video
│   ├── temp\                  ← ffmpeg working dir (run HERE) + fonts\ (Montserrat Bold; Anton legacy)
│   └── final clips\           ← Outputs ONLY (category\lang\video subfolders)
│       └── [category]\[lang]\[Video Title]\
│           ├── ass\
│           ├── clips\
│           ├── metadata\
│           └── upload_sheet.txt
└── system\
    ├── references\            ← tool-routing, encoding, captions, errors
    ├── youtube-mcp-server\    ← MCP #1: Upload + SEO audit (13 tools)
    ├── youtube-mcp-seo\       ← MCP #2: SEO + Analytics (16 tools)
    ├── prompt.md              ← The prompt
    ├── rules.md               ← Trigger rules
    ├── SKILL.md               ← Pipeline spec
    └── youtube.md             ← This file

## MCP Stack (2 servers, all free, all local — video work = FFmpeg CLI)

| Server | Tools | Role |
|--------|-------|------|
| youtube | 13 | Upload, SEO audit, analytics (A/B + set_thumbnail tools exist but unused here) |
| youtube-seo | 16 | SEO score, tag analysis, keywords, trends |

System CLIs (not MCP): yt-dlp (download), ffmpeg + ffprobe (every edit, QC), MediaPipe (Mode A face track, inline python -c).
Total: 29 MCP tools + CLIs. $0. No cloud.

## Mode Selection (per VIDEO content type)

| Content type | Mode | Technique |
|--------------|------|-----------|
| MrBeast / Extreme / Action | Mode B (default) | 3-zone blurred bg: fg fill-crop 1080×864 hero band over gblur'd darkened fill |
| Vlog / Travel | Mode B | Blurred bg |
| Podcast / Interview (single person) | Mode A | Face-track crop (608:1080) + silenceremove -af |
| Movies (extract clips) | Center-crop | crop=ih*9/16 formula (auto-adjusts) |
| Gaming / Screen | Center-crop | Fixed center crop |
| Multi-language (Hindi/ES) | Any mode | Same English ASS both channels — only `-i` source changes. Captions always English Montserrat Bold (Captions Rule) |

Exact commands: references\tool-routing.md → Stage 4.

## Hindi/Hinglish Support

| Setting | Value |
|---------|-------|
| Font | Montserrat Bold 96px (English captions — Captions Rule). Never Mangal, never Hindi ASS |
| Active captions | Yellow (#FFE500), per caption-styles.md |
| yt-dlp subs | `--write-subs --sub-lang hi,en --convert-subs srt` |
| ASS filter | Use `ass=` filter (not subtitles) — preserves matras |

## Encoding Settings

| Setting | Value |
|---------|-------|
| Mode B bg | scale-fill 1080x1920 + gblur sigma=40 + brightness -0.25 |
| Mode B fg | scale=1080:864:increase + crop=1080:864 (fill) → overlay 0:384 (384/864/672 zones, 20/45/35) |
| Mode A crop | crop=608:1080:'<MEDIAPIPE_EXPRESSION>':0 (1920x1080 input) |
| Center-crop | crop=ih*9/16:ih:(iw-ih*9/16)/2:0 (dynamic — never hardcode pixels) |
| Scale (crop/A mode) | 1080:1920:flags=lanczos |
| Video codec | libx264 CRF 18 preset ultrafast |
| Audio codec | AAC 192kbps 48kHz |
| Loudness | loudnorm=I=-14:TP=-1:LRA=11 |
| Podcast -af | silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.5 (before afade) |
| Captions | ass='NN.ass':fontsdir='fonts' — Montserrat Bold 96px, #FFE500, per-line \an8\pos + \fsp-0.5 (caption-styles.md v2.3) |
| Hook banner | pill PNG (1080×120 r50) at y=84 + Montserrat Bold 40px black on the pill canvas (textfile=, W/H of pill) — UNIQUE title per clip (prompt.md Hook Title Rule), t=1–15 with 0.5s alpha fades |
| Video fade | in 0.5s, out 1.5s (st=$DUR-1.5) |
| Audio fade | in 0.5s, out 1s (st=$DUR-1) |
| Flags | +faststart yuv420p |

One ffmpeg pass per clip = mode composite + captions + hook + loudnorm + fades + export.
Exact command: references/tool-routing.md → Stage 4. Run from D:\youtube system\output\temp.

## Clip Rules

- Duration: 70 seconds fixed (QC gate 65-120s — rules.md)
- Count: 15-18 per video (~90% coverage)
- Boundaries: Natural sentence breaks + ffmpeg scene detect
- Hook: UNIQUE title per clip = that segment's most shocking line (max 8 words, ALL CAPS — prompt.md Hook Title Rule) · pill PNG at y=84, t=1–15 (0.5s fades)
- Captions: Custom ASS (Montserrat Bold 96px, #FFE500, per-line \an8\pos + \fsp-0.5, ACTIVE_RISE — references/caption-styles.md v2.3)
- Color: Mode B bg eq brightness -0.25 (crop/A modes: eq=contrast=1.05:saturation=1.08)
- Spread: Evenly across full video duration
- Exclude: Sponsor segments

## Backup (only if no SRT exists)

Use yt-dlp `--write-subs --sub-lang hi,en` first. If no SRT available: ask user, then FunClip transcription backup.

## Rollback

If components fail:
- YouTube MCP fail → manual upload via Studio
- SEO MCP fail → skip scoring, upload as-is
- FFmpeg missing/broken → check D:\FunClip\tools\ffmpeg\bin\ on PATH, tell user, STOP
- MediaPipe missing → only Mode A affected → `pip install mediapipe`; center-crop/Mode B unaffected
