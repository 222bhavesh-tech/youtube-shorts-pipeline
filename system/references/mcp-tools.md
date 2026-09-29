# MCP Tools Reference

**kinocut REMOVED from this project.** All video work = FFmpeg 9.0.1 (ONE pass per clip) at `D:\FunClip\tools\ffmpeg\bin\` (= PATH). Mode A/B routing + exact command: tool-routing.md Stage 4.

## System CLIs (NOT MCP — all editing/analysis lives here)

### Stage 1: Download
```
yt-dlp            → 4K video + SRT download
```

### Stage 2: Analyze Source
```
ffprobe           → width, height, codec, fps, duration
ffmpeg scene      → -vf "select='gt(scene,0.3)',showinfo" → cut boundaries
ffmpeg silence    → -af "silencedetect=n=-30dB:d=1" → silence gaps
```

### Stage 4: Encode (ONE pass per clip)
```
ffmpeg            → trim + 9:16 crop/scale + ASS burn + hook drawtext + eq color
                    + loudnorm + video/audio fades + export (CRF 18)
                    → exact command: tool-routing.md Stage 4
```

### Stage 5: QC
```
ffprobe           → 1080x1920, h264, 65-120s (target 70s), aac present, file exists
```

## YouTube (13 tools)

### Upload
```
youtube_upload    → { file_path, title, description, tags, privacy } → { success, video_id, url }
youtube_whoami    → {} → { channel_id, channel_name, subscribers }
youtube_playlist_add → { playlist_id, video_id } → { success }
```

### Analytics
```
youtube_ab_report → { video_id } → { results }
youtube_ab_rotate → { video_id } → { success }
```

## YouTube-SEO (16 tools)

### Analysis
```
get_video_details → { video_id } → { title, description, tags, views, likes }
get_video_seo_score → { video_id } → { score, issues: [...] }
analyze_thumbnail → { video_id } → { url, resolution, size }
```

### Channel
```
get_channel_overview → {} → { subscribers, videos, views }
```

> Note: `get_video_seo_score` takes only `video_id` — usable AFTER upload. Pre-upload SEO = manual checklist (tool-routing.md Stage 6).
