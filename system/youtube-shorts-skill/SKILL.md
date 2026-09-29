---
name: youtube-shorts-pipeline
description: |
  Full YouTube Shorts automation: download, transcribe, cut viral moments,
  encode with animated captions, SEO optimize, and auto-upload.
  Use when user says "youtube system" or provides a YouTube URL for Shorts creation.
---

## Trigger

When user types "youtube system" or provides a YouTube URL for Shorts:

"Hello Sir! What would you like to do?
1. **YouTube Link** — I will download and run the full pipeline
2. **Personal File** — Provide video path (skip download)"

## Required MCP Servers

This skill requires 3 MCP servers to be configured:

| MCP | Install | Tools |
|-----|---------|-------|
| kinocut | `python -m kinocut` | 196 (video editing) |
| youtube | `python "D:\youtube system\system\youtube-mcp-server\server.py"` | 13 (upload, A/B) |
| youtube-seo | `python "D:\youtube system\system\youtube-mcp-seo\server.py"` | 16 (SEO, analytics) |

## Required Tools (system)

- FFmpeg (on PATH)
- yt-dlp (`pip install yt-dlp`)
- Python 3.12+

## Pipeline

### Option 1: YouTube URL

1. **Download**: yt-dlp best 4K video + English SRT
2. **Analyze**: kinocut video_info + scene_detect + waveform
3. **Select**: Read SRT, pick 15-18 viral moments (75-85s, natural boundaries)
4. **Encode** (per clip):
   - Dynamic crop (16:9→9:16, 9:16→passthrough, 1:1→pad)
   - scale=1080:1920:flags=lanczos
   - Word-by-word ASS captions (ALWAYS English, Montserrat Bold 96px font — SAME ASS for EN and HI; never Mangal)
   - color_grade: consistent LUT
   - silence_removal >1s
   - loudnorm=I=-14:TP=-1.5:LRA=11
   - fade in/out (video in 0.5s / out 1.5s, audio in 0.5s / out 1s — rules.md Fades)
   - libx264 CRF 16 preset slow, AAC 192k, +faststart
5. **QC**: release_checkpoint per clip, video_rescue if FAIL
6. **Metadata**: SEO title, description, tags (LLM writes)
7. **SEO Score**: youtube-seo score, revise if <70
8. **Upload**: youtube MCP upload (private, no custom thumbnails)
9. **Cleanup**: delete temp, keep outputs

### Option 2: Personal File

Skip Step 1. User provides video path (+ optional SRT path).
If no SRT: ask, or use FunClip/Whisper backup.
Continue from Step 2.

## Folder Structure

```
D:\youtube system
├── output\
│   ├── 4k video\          ← Source (Option 1), per language: en\ hi\
│   ├── transcript\        ← SRT (Option 1), per language: en\ hi\
│   ├── face_track\        ← Crop expressions, per language: en\ hi\, prefixed per video
│   ├── temp\              ← ffmpeg working dir + fonts\
│   └── final clips\       ← Outputs ONLY (category\lang\video)
│       └── [category]\[lang]\[Video Title]
│           ├── ass
│           ├── clips
│           ├── metadata
│           └── upload_sheet.txt
└── system\
    ├── youtube-mcp-server
    ├── youtube-mcp-seo
    ├── prompt.md
    └── youtube.md
```

## Encoding Settings

| Setting | Value |
|---------|-------|
| Crop (16:9) | crop=ih*9/16:ih:(iw-ih*9/16)/2:0 |
| Scale | 1080:1920:flags=lanczos |
| Video | libx264 CRF 16 preset slow |
| Audio | AAC 192k 48kHz |
| Loudness | I=-14 TP=-1.5 LRA=11 |
| Fades | Video 1s, Audio 0.5s |
| Flags | +faststart yuv420p |

## Clip Rules

- 75-85s each, 15-18 per video
- Natural sentence boundaries
- Hook in first 3s
- Exclude sponsors
- Spread evenly across full duration

## Language Support

- English: Montserrat Bold font (caption-styles.md v2.3)
- Captions: ALWAYS English + Montserrat Bold 96px (Captions Rule) — never Mangal, never Hindi ASS
- Any: Use appropriate script font in ASS
