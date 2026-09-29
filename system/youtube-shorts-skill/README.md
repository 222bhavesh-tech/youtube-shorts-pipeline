# YouTube Shorts Pipeline

One URL in → 15-18 viral Shorts out. Auto-uploaded to YouTube.

## Install

```
setup.bat
```

## Configure MCP (any agent)

Add to your agent's MCP config:

```json
{
  "mcpServers": {
    "kinocut": { "command": "python", "args": ["-m", "kinocut"] },
    "youtube": { "command": "python", "args": ["D:\\youtube system\\system\\youtube-mcp-server\\server.py"] },
    "youtube-seo": { "command": "python", "args": ["D:\\youtube system\\system\\youtube-mcp-seo\\server.py"] }
  }
}
```

## Use

Tell your agent: `"youtube system"`

Then provide a YouTube URL or local file path.

## Works with

OpenCode, Claude Code, Cursor, Codex, Windsurf, VS Code, Antigravity, Zed, GitHub Copilot

## What it does

1. Downloads 4K video + subtitles via yt-dlp
2. Analyzes scenes and audio with kinocut (196 tools)
3. Picks 15-18 viral moments from transcript
4. Encodes each clip (9:16, captions, color grade, loudness)
5. Quality checks every clip
6. SEO scores and optimizes metadata
7. Uploads to YouTube
8. Reports results

## Folder Structure

```
D:\youtube system\
├── output\
│   ├── 4k video\          ← Source downloads, per language: en\ hi\
│   ├── transcript\        ← SRT files, per language: en\ hi\
│   ├── face_track\        ← Crop expressions, per language: en\ hi\, prefixed per video
│   ├── temp\              ← ffmpeg working dir + fonts\
│   └── final clips\       ← Outputs (category\lang\video)
│       └── [category]\[lang]\[Title]\
│           ├── clips\     ← Encoded Shorts
│           ├── ass\       ← Captions
│           ├── metadata\
│           └── upload_sheet.txt
└── system\
    ├── prompt.md          ← Copy-paste prompt
    ├── youtube.md         ← Reference docs
    ├── youtube-mcp-server\
    └── youtube-mcp-seo\
```

## License

MIT
