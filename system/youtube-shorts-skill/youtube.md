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
│  • Orchestrates all MCP calls                           │
└──────┬──────────────────┬──────────────────┬────────────┘
       ▼                  ▼                  ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────────┐
│   yt-dlp    │  │  Kinocut MCP │  │  YouTube MCP     │
│  (download) │  │  (196 tools) │  │  (13 tools)      │
└─────────────┘  └──────────────┘  └──────────────────┘
                                 ┌──────────────────┐
                                 │  YouTube-SEO MCP │
                                 │  (16 tools)      │
                                 └──────────────────┘

## Folder Structure

D:\youtube system\
├── output\
│   ├── 4k video\          ← Source (yt-dlp downloads), per language: en\ hi\
│   ├── transcript\        ← SRT files, per language: en\ hi\ — captions always read en\
│   ├── face_track\        ← Crop expressions, per language: en\ hi\, prefixed per video
│   ├── temp\              ← ffmpeg working dir + fonts\
│   └── final clips\       ← Outputs ONLY (category\lang\video subfolders)
│       └── [category]\[lang]\[Video Title]\
│           ├── ass\
│           ├── clips\
│           ├── metadata\
│           └── upload_sheet.txt
└── system\
    ├── youtube-mcp-server\  ← MCP #1: Upload + SEO audit (13 tools)
    ├── youtube-mcp-seo\     ← MCP #2: SEO + Analytics (16 tools)
    ├── prompt.md            ← The prompt
    └── youtube.md           ← This file

## MCP Stack (3 servers, all free, all local)

| MCP | Tools | Role |
|-----|-------|------|
| kinocut | 196 | Video editing (crop, captions, loudnorm, encode, QC) |
| youtube | 13 | Upload, SEO audit, analytics (A/B + set_thumbnail tools exist but unused here) |
| youtube-seo | 16 | SEO score, tag analysis, keywords, trends |

Total: 225 tools. $0. No cloud.

## Hindi/Hinglish Support

| Setting | Value |
|---------|-------|
| Font | Montserrat Bold 96px (English captions — Captions Rule). Never Mangal |
| Active word | Yellow (#FFE500), scale 110% |
| Inactive word | White, black outline 4px |
| yt-dlp subs | `--write-subs --sub-lang hi,en --convert-subs srt` |
| ASS filter | Use `ass=` filter (not subtitles) — preserves matras |

## Encoding Settings

| Setting | Value |
|---------|-------|
| Crop | crop=1216:2160:1312:0 (center 9:16 from 4K) |
| Scale | 1080:1920:flags=lanczos |
| Video codec | libx264 CRF 16 preset slow |
| Audio codec | AAC 192kbps 48kHz |
| Loudness | loudnorm=I=-14:TP=-1.5:LRA=11 |
| Video fade | in 0.5s, out 1.5s (st=$DUR-1.5) |
| Audio fade | in 0.5s, out 1s (st=$DUR-1) |
| Flags | +faststart yuv420p |

## Clip Rules

- Duration: 75-85 seconds
- Count: 15-18 per video (~90% coverage)
- Boundaries: Natural sentence breaks only
- Hook: Best line in first 3 seconds
- Captions: Word-by-word animated ASS (ALWAYS English, Montserrat Bold 96px, yellow active — SAME ASS for EN and HI)
- Color grade: Consistent warm cinematic LUT across all clips
- Spread: Evenly across full video duration
- Exclude: Sponsor segments

## Backup (only if no SRT exists)

Use yt-dlp `--write-subs --sub-lang hi,en` first. If no SRT available, the pipeline will note missing transcripts.

## Installed Tools

| Tool | Location |
|------|----------|
| FFmpeg | System (used by kinocut) |
| Python 3.12 | System |
| yt-dlp | pip (system) |
| kinocut | pip (python -m kinocut) |
| Montserrat Bold | English captions (Captions Rule) — Mangal banned |

## Rollback

If MCPs fail:
- Kinocut gap → use ffmpeg-skill (still installed)
- YouTube MCP fail → manual upload via Studio
- SEO MCP fail → skip scoring, upload as-is
