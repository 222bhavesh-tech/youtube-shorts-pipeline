# Tool Routing — EXACT Tool per Stage (No Guessing)

## RULE: Agent MUST use ONLY the tools listed below. No alternatives. No improvising.

## STACK (kinocut REMOVED from this project — not required)
- System CLIs: yt-dlp (download), ffmpeg + ffprobe (ALL video work)
- MCP: youtube (13), youtube-seo (16) — upload + SEO only
- Encode binary: WinGet Gyan **7.1.1-full_build** — `C:\Users\bhavesh jeengar\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe`
- PATH ffmpeg/ffprobe (`D:\FunClip\tools\ffmpeg\bin\`) = **analysis + QC only** (9.0.1), never encode

═══════════════════════════════════════════════════════════
STAGE 1: DOWNLOAD
═══════════════════════════════════════════════════════════

| Step | Tool | Command | MCP? |
|------|------|---------|------|
| Download video EN | yt-dlp (system CLI) | `yt-dlp -f "bv*+ba[language=en]" -o "D:\youtube system\output\4k video\en\%(title)s [%(id)s].%(ext)s" "URL"` | No |
| Download video HI | yt-dlp (system CLI) | `yt-dlp -f "bv*+ba[language=hi]" -o "D:\youtube system\output\4k video\hi\%(title)s [%(id)s].%(ext)s" "URL"` | No |
| Download SRT EN | yt-dlp (system CLI) | `yt-dlp --write-subs --skip-download --sub-lang en --convert-subs srt -o "D:\youtube system\output\transcript\en\%(title)s [%(id)s].%(ext)s" "URL"` | No |
| Download SRT HI | yt-dlp (system CLI) | `yt-dlp --write-subs --skip-download --sub-lang hi --convert-subs srt -o "D:\youtube system\output\transcript\hi\%(title)s [%(id)s].%(ext)s" "URL"` | No |
| Check if exists | Python (os.path) | `if os.path.exists(path): skip` | No |

## RULE: If yt-dlp fails → STOP. Tell user. Do NOT proceed.

## No SRT Fallback (agent handles entirely, user does nothing)

No SRT found (URL or local file) → FunClip backup runs automatically. NEVER skip Stage 3 without a transcript. (If user manually provides an SRT, use it directly.)

| Step | Who | Action |
|------|-----|--------|
| 1 | Agent | Detects no SRT |
| 2 | Agent | Checks if FunClip running: port 7860 listening — PowerShell `Get-NetTCPConnection -LocalPort 7860 -State Listen` (curl is BLOCKED in this environment) |
| 3 | Agent | If not running: starts `run_funclip_headless.bat` (background, `--lang en` baked in) |
| 4 | Agent | Waits for server — max 150s (model load measured 105–135 s; log `%TEMP%\funclip_err.log`) |
| 5 | Agent | Calls gradio_client → `/mix_recog` (FunClip has NO `/transcribe` endpoint): `D:\FunClip.venv\Scripts\python.exe` → `c.predict({'video': handle_file(vid)}, None, '', tmp_out, api_name='/mix_recog')` → returns `(transcript_text, srt_text, txt_file, srt_file)` |
| 6 | Agent | Saves SRT to `output\transcript\en\[Title].en.srt` (move ONLY the `.srt` from tmp_out) → convert to `transcript\en\plain.txt` (Captions Rule — gen_ass reads plain.txt, L73) |
| 7 | Agent | Generates outline.md |
| 8 | Agent | Continues from Stage 3 |

## RULE: User is NEVER asked to open a browser, click a button, or interact with FunClip.
## RULE: This is fully automated. User only sees: "Transcribing... done."

What user sees (only this):

    Agent: "No SRT found. Transcribing with FunClip... (~2 min)
           ✅ Done. Continuing pipeline..."

That's it. No browser. No GUI. No "open localhost:7860". No manual action. Agent does everything. User just waits.

Verified call details (2026-09-25, live-tested):
- Use the **FunClip venv python** for the client (gradio_client 1.3.0 ↔ server gradio 4.44.1); system python's gradio_client 2.7.1 is a mismatched major version.
- Video arg MUST be `{'video': handle_file(path)}` — bare `handle_file()` → `VideoData.video Field required`. `audio=None`, `hotwords=''` work.
- Speed ≈ 3× realtime (86 s clip → 27–34 s; 2 h movie ≈ 40–50 min). `tmp_out` also receives `result_*.txt` + `1best_recog\` — move ONLY the `.srt`.
- EN model is good for selecting moments but a few cue words come out wrong → proofread cue text before burning captions.
- Stop FunClip after transcription (shares GPU with encodes): kill the python process running `funclip\launch.py`. Next no-SRT run restarts it (step 3).

═══════════════════════════════════════════════════════════
STAGE 2: ANALYZE
═══════════════════════════════════════════════════════════

| Step | Tool | MCP? | Exact Call |
|------|------|------|------------|
| Probe source | ffprobe | No (CLI) | `ffprobe -v error -select_streams v:0 -show_entries stream=width,height,codec_name,r_frame_rate -show_entries format=duration -of default=noprint_wrappers=1 SRC` |
| Scene boundaries | ffmpeg | No (CLI) | `ffmpeg -i SRC -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | Select-String pts_time` |
| Silence gaps | ffmpeg | No (CLI) | `ffmpeg -i SRC -af "silencedetect=n=-30dB:d=1" -f null - 2>&1 | Select-String silence_` |

## RULE: Snap clip boundaries to ffmpeg scene cuts / silence gaps. Do NOT pick random timestamps.

═══════════════════════════════════════════════════════════
STAGE 3: SELECT MOMENTS
═══════════════════════════════════════════════════════════

| Step | Tool | MCP? | Details |
|------|------|------|---------|
| Read transcript | OpenCode LLM | No | Full SRT read from `transcript\en\` (captions + moments ALWAYS EN — Captions Rule), pick 15-18 moments (prompt.md) |
| Boundary snap | OpenCode LLM | No | START = SRT cue entry; END = scene cut |
| Exclude sponsor | OpenCode LLM | No | "sponsor", "sponsored by", "thanks to" |

## RULE: DUR 70s per clip (variable $DUR — target 70, sentence-snap window 65–75s, QC gate 65–120s). First 0.5s = hook. Clips NEVER overlap. No sponsor overlap. NEVER >120s. (Full spec applies on `redo`.)

═══════════════════════════════════════════════════════════
STAGE 4: ENCODE (ONE pass per clip)
═══════════════════════════════════════════════════════════

**Run from:** `D:\youtube system\output\temp` (drive-colon paths break ffmpeg's filter parser — relative paths inside filters only; absolute paths OK as `-i` inputs).
**GPU: Quadro P620 2GB → max 2 encodes running at a time. Clear inherited `CUDA_VISIBLE_DEVICES=-1` first (`$env:CUDA_VISIBLE_DEVICES = $null`) or NVENC silently falls back/fails.**
**Template — replace ALL placeholders (NN/CATEGORY/LANG/TITLE/START) before running.**

**Captions Rule (every encode):**
- ASS file: ALWAYS English, ALWAYS Montserrat Bold font (caption-styles.md v2.3 — Anton retired)
- Same ASS file used for both EN and HI clips
- Only `-i` audio source changes (EN audio file vs HI audio file) — `4k video\en\SRC.mp4` vs `4k video\hi\SRC.mp4`
- Do NOT translate captions · Do NOT use Mangal · Do NOT generate Hindi ASS

**Mode selection (per video content type):**

| Mode | Content | Technique |
|------|---------|-----------|
| A | Single person, face visible (podcast, vlog, talking) | MediaPipe face-track → dynamic crop follows face |
| B (default) | Wide/multi-person/action (extreme, sports, movies) | Blurred fill bg (gblur σ40 + eq −0.25) + hero band 1080:864 `overlay=0:384` + face-crop close-up overlay (enable ranges) — canonical dual A+B graph, encoding-settings.md |
| Center-crop | Gaming, already 9:16 | `crop=ih*9/16:ih:(iw-ih*9/16)/2:0` only |

**Prep (per clip):**
- `python face_track_analyze.py <start_sec> <dur_sec> <clipNN>` → writes `output\face_track\en\<TAG>_cropNN.txt` + `<TAG>_trackNN.json` (defaults: SRC `4k video\en\…`, OUTDIR `output\face_track\en\`; argv[4]=SRC, argv[5]=OUTDIR, argv[6]=TAG — pass `…\hi\` paths for a HI source). Engine = **MediaPipe 1.0.1 FaceLandmarker VIDEO mode** (478-pt, per-frame temporal tracking → ~3× smoother crop-x, fewer face-dropouts than legacy BlazeFace; `system\assets\models\face_landmarker.task`); auto-falls back to BlazeFace `FaceDetector` if the landmarker can't init, `FACE_TRACK_ENGINE=detector` forces legacy.
- `python gen_ass.py <start_sec> <end_sec> <out.ass>` (run from project dir; argv[4] = transcript override, default `output\transcript\en\plain.txt` — ALWAYS the EN transcript, Captions Rule) → writes `temp\NN.ass` at temp root

**Overlay steps — Top Overlay Timeline (rules.md, STACKED: each enters then STAYS), all inside the ONE pass:**

| Step | Overlay | Tool | Exact settings |
|------|---------|------|----------------|
| 4a | Hook pill | ffmpeg | `-framerate 30 -loop 1 -t $DUR` input, drawtext on pill canvas, `fade in@1 / out@14.5 (alpha)`, overlay x=0 y=84, enable='between(t,1,15)' |
| 4b | like-comment-subscribe | ffmpeg | `format=rgba,setpts=PTS+25/TB` (NO hold — full 5s plays 25→30, ends empty → auto-removed), overlay x=268 y=56 (content center (540,192), middle of 0–384 zone), enable='gte(t,25)' |
| 4c | notification bell | REMOVED permanently 2026-09-26 (froze to clip end) — never re-add |
| 4d | youtube-subscribe | REMOVED permanently 2026-09-26 (froze to clip end) — never re-add |
| 4e | center-subscribe (MAIN band) | ffmpeg | `scale=991:-2,loop=loop=-1:size=1:start=296,scale=w='max(2,991*K)':h=-2:eval=frame` (loop-hold on last VISIBLE frame f296 — asset tail is empty), overlay x='44.5+495.5*(1-K)' y='534.6+279*(1-K)', enable='between(t,60,69.4)' — +20% size (user 2026-09-29), K-bounce in 60→60.3 / out 69→69.3, gone after 69.4, global end fade covers clip end |

**Mode B command (PowerShell, ONE pass — no `^` continuations):**
```powershell
$env:CUDA_VISIBLE_DEVICES = $null
$ffmpeg = 'C:\Users\bhavesh jeengar\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe'
$vfade = [math]::Round($DUR - 1.5, 3); $afade = [math]::Round($DUR - 1, 3)
$fc = @"
[1:v]format=rgba,drawtext=fontfile='fonts/montserrat-bold.ttf':textfile='hookNN.txt':fontsize=40:fontcolor=black:x='(W-text_w)/2':y='(H-text_h)/2',fade=t=in:st=1:d=0.5:alpha=1,fade=t=out:st=14.5:d=0.5:alpha=1[hook];
[0:v]split=3[fa0][fb0][fg0];
[fa0]crop=608:1080:x='<EXPR>':y=0,scale=1080:1920:flags=lanczos[fa];
[fb0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.25[fb];
[fg0]scale=1080:864:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:864[fg];
[fb][fg]overlay=0:384[wide];
[wide][fa]overlay=0:0:enable='<close ranges>'[vbase];
[vbase]ass='NN.ass'[sub];
[sub][hook]overlay=0:84:enable='between(t,1,15)'[t1];
[2:v]format=rgba,setpts=PTS+25/TB[lcs];
[t1][lcs]overlay=x=268:y=56:enable='gte(t,25)'[t2];
[3:v]format=rgba,scale=991:-2,loop=loop=-1:size=1:start=296,scale=w='max(2,991*K)':h=-2:eval=frame[cs];
[t2][cs]overlay=x='44.5+495.5*(1-K)':y='534.6+279*(1-K)':enable='between(t,60,69.4)'[t3];
[t3]fade=t=in:st=0:d=0.5,fade=t=out:st=${vfade}:d=1.5,fps=30000/1001,format=yuv420p[vout];
[0:a]loudnorm=I=-14:TP=-1:LRA=11,afade=t=in:st=0:d=0.5,afade=t=out:st=${afade}:d=1[aout]
"@
& $ffmpeg -y -ss <START> -t $DUR -i "4k video\<lang>\SRC.mp4" -framerate 30 -loop 1 -t $DUR -i "D:\youtube system\system\assets\hook_pill.png" `
  -i "D:\youtube system\system\assets\overlays\like-comment-subscribe.mp4" `
  -i "D:\youtube system\system\assets\overlays\center-subscribe.mov" `
  -filter_complex $fc -map "[vout]" -map 0:a `
  -c:v h264_nvenc -preset p5 -rc vbr -cq 18 -b:v 0 -spatial-aq 1 `
  -c:a aac -b:a 192k -ar 48000 -pix_fmt yuv420p -movflags +faststart `
  -t $DUR `
  "final clips\CATEGORY\LANG\TITLE\clips\NN_slug.mp4"
```
- The CS `loop=-1` hold makes the center-subscribe stream **infinite** → the output `-t $DUR` is REQUIRED (and the pill input needs its own `-t $DUR` to stop the loop). The hold is `loop=loop=-1:size=1:start=296` — f296 is the measured last-VISIBLE frame; the asset's f297-299 tail is empty (never hold true EOF). LCS is NOT held: `format=rgba,setpts=PTS+25/TB` — plays 25→30, empty tail repeats invisibly.
- `-map 0:a` only — overlay streams are NEVER mapped.
- `<close ranges>` = `enable_expr` from `<TAG>_trackNN.json`. No close-up ranges for that clip → drop the `[wide][fa]` overlay line entirely.
- `<EXPR>` = crop expression from `<TAG>_cropNN.txt`. Do NOT hand-roll a chained `if()` — expression nesting >98 → `-22 Failed to configure input pad`.
- Inputs: exactly 4 — 0 = source video, 1 = `hook_pill.png` (1080×120 r50, looped `-framerate 30 -loop 1 -t $DUR`), 2 = `assets\overlays\like-comment-subscribe.mp4` (544×272, 5s file — plays IN FULL, no freeze), 3 = `assets\overlays\center-subscribe.mov` (PNG/RGBA 3840×2160 30fps **exactly 10.000s, clear background, tail f297-299 empty** — enters at 60, loop-held across the 60→69.4 window). **notification-bell.mov + youtube-subscribe.mp4 are REMOVED permanently (user 2026-09-26: "remove notification bell and Subscribe (YS) permanently" — they froze in place to clip end instead of exiting smoothly) — never re-add.** The remaining overlays are the ONLY allowed ones = Top Overlay Timeline (rules.md, STACKED): 4a hook `between(t,1,15)` with alpha fades, 4b LCS `format=rgba,setpts=PTS+25/TB` + `enable='gte(t,25)'` (full 5s plays, auto-removes), 4e CS `scale=991:-2,loop=loop=-1:size=1:start=296,scale=w='max(2,991*K)':h=-2:eval=frame` + `enable='between(t,60,69.4)'` at **x='44.5+495.5*(1-K)' y='534.6+279*(1-K)' (MAIN band center, +20% size per user 2026-09-29)**. **`loop=loop=-1:size=1:start=296` is REQUIRED** for CS — without a hold the asset's empty tail (and EOF) repeats, so the button dies ~0.1s before 70 and stays dead on clips longer than 70 (clips run to 74.7s); `loop=size=1` repeats ONLY the last visible frame (no bounce replay), verified gap-free to 75.9s. `x=268` centers the 544px cards (544→268..812); pill is full width → x=0. LCS: NO fade/scale/opacity (rules.md "Overlay Animation") — the file's own animation is the only look. Old CTA assets (`system\assets\overlays\cta\`) stay deleted. ASS, hook text, fonts all live at `temp\` root (`NN.ass`, `hookNN.txt`, `fonts\montserrat-bold.ttf`) — cwd-relative, never `v2ass\`.

**Mode A differences:** no gblur/eq/bg zones — `[0:v]` runs only the face-track crop → `scale=1080:1920:flags=lanczos`.

**Export flags:** `-movflags +faststart -pix_fmt yuv420p` · AAC 192k 48kHz · input-seek `-ss START -t DUR` · `fps=30000/1001`.

## RULE: ONE ffmpeg pass per clip. Nothing chained. Nothing else touches the file.

═══════════════════════════════════════════════════════════
STAGE 5: QUALITY GATE (per clip)
═══════════════════════════════════════════════════════════

Run on the REAL file: `final clips\CATEGORY\LANG\TITLE\clips\NN_slug.mp4`. **h264 output only** — QC fails on any other video codec.

| # | Check | Exact Call / Criterion |
|---|-------|------------------------|
| 1 | Streams + format | `ffprobe -v error -show_entries stream=index,codec_name,width,height,pix_fmt,avg_frame_rate,sample_rate -show_entries format=duration,size -of default=noprint_wrappers=1 OUT` → **exactly 2 streams** |
| 2 | Video codec | `codec_name` = **h264** |
| 3 | Resolution | **1080x1920** |
| 4 | Pixel format | **yuv420p** |
| 5 | Frame rate | `avg_frame_rate` exactly **30000/1001** |
| 6 | Audio | **aac**, `sample_rate` **48000** |
| 7 | Duration | `format=duration` in **65–120 s** (target **70 s** — legacy 75–120s videos also pass) |
| 8 | Size | `format=size` **< 2 GB** |
| 9 | Last-frame YAVG | `ffmpeg -i OUT -sseof -0.3 -vf "signalstats,metadata=print:key=lavfi.signalstats.YAVG" -f null -` → **YAVG 14.5–22** (black/blown ending = fade bug) |
| 10 | Loudness | `ffmpeg -i OUT -af ebur128 -f null -` → integrated **I within 0.6 LU of −14** |

**QC fail routing:**
- FAIL → ffprobe the real file (path above). Not 4:3 → STAGE 4 bug (Mode) → tool-routing.md Stage 4.
- 4:3 but ffprobe says 1080x1920 → last-frame YAVG out of 14.5–22 (black or blown ending) → re-encode that clip once with corrected fades (Stage 4).
- Audio drift / loudness fail → AAC sample-rate or loudnorm → check `-ar 48000` + `loudnorm=I=-14:TP=-1:LRA=11` in Stage 4.

Re-run the Stage 4 command with new input ranges. Do NOT edit the MP4.

═══════════════════════════════════════════════════════════
STAGE 6: METADATA + SEO
═══════════════════════════════════════════════════════════

| # | Step | Tool | MCP? | Exact Call |
|---|------|------|------|------------|
| 1 | Write title | OpenCode LLM | No | 100 chars max, keyword first, ALL CAPS hook word |
| 2 | Write description | OpenCode LLM | No | 2-3 lines + #Shorts + 3-5 hashtags |
| 3 | Write tags | OpenCode LLM | No | 10-15 tags |
| 4 | Save file | Python (open/write) | No | `final clips\CATEGORY\LANG\TITLE\metadata\NN.txt` |

**Pre-upload SEO checklist (manual — `get_video_seo_score` needs a video_id, so NOT possible pre-upload):**
- Title ≤100 chars, keyword in first 5 words, ALL CAPS hook word
- Description: line 1 = hook (shows before "...more"), line 2 = context, line 3 = #Shorts + hashtags
- Tags: 10-15, mix broad ("shorts", "viral") + specific ("desert survival", "7 days underground")
- Checklist <70 → revise title/desc/tags (max 2 cycles)

## RULE: QC gate (Stage 5) BEFORE metadata — no point writing SEO for a dead file. Metadata + SEO must be final before a clip enters Stage 7 (upload).

═══════════════════════════════════════════════════════════
STAGE 7: UPLOAD (AUTHORIZED ONLY)
═══════════════════════════════════════════════════════════

## PHASE A — SHOW AND WAIT (after Stage 6, before ANY upload)

Show user exactly this (verdict paths at final location):

```
All 43 clips ready. Review them:
D:\youtube system\output\final clips\[category]\[lang]\[short name]\clips\NN_slug.mp4
Say 'pass' to upload. Say 'redo 03' to re-encode clip 03.
```

→ WAIT. Do NOT proceed. Do NOT upload. Do NOT do anything else.

## PHASE B — CONTROL POINTS (act ONLY on these exact commands)

| User says | Agent does |
|-----------|-----------|
| `pass` | Upload ALL |
| `pass 01 02 05` | Upload ONLY those 3 |
| `redo 03` | Re-encode clip 03, show again |
| `redo 03 07` | Re-encode both, show again |
| `skip 05` | Remove from upload list |
| `stop` | Halt. Nothing uploads. |
| anything else | Ask user to clarify. Still WAIT. |

**Until every clip has an explicit `pass NN` / `skip NN` / `redo NN` (or a blanket `pass`), nothing goes to YouTube. Period.**

After `redo` → re-encode specified clips → show updated list → WAIT again.
After `skip` → show updated list → WAIT again (skip does NOT trigger upload).

## PHASE C — UPLOAD (only after explicit verdicts)

| # | Phase | Tool | MCP? | Exact Call |
|---|-------|------|------|------------|
| 1 | Verify entitlement | youtube_whoami | youtube | `youtube_whoami()` → {channel_id, title, videoCount} — if videoCount null → treat as unverified |
| 2 | Upload | youtube_upload | youtube | `youtube_upload(file_path=PATH, title=T, description=D, tags=TAGS, category_id="22", privacy="private")` → str with video_id/url/privacy. NO `language` param, NO media-object second arg. First upload triggers Google OAuth. |
| 3 | Record | OpenCode LLM | No | Append video_id + url to `final clips\CATEGORY\LANG\TITLE\upload_sheet.txt` |

**Entitlement check (Stage 7 rule):**
```
If whoami.videoCount is null AND channel is <48h old → manual verification required:
  - Phone verify unlocks custom thumbnails only
  - 100 subs + 3 uploads unlocks "Made for Kids" setting API
  - Uploads DO work immediately for standard videos → proceed
```

## RULE: Do NOT call youtube_upload until the user's verdict command. NEVER upload before Phase A. NEVER skip the WAIT. No exceptions.

═══════════════════════════════════════════════════════════
STAGE 8: POST-UPLOAD SEO
═══════════════════════════════════════════════════════════

| # | Tool | MCP? | Exact Call |
|---|------|------|------------|
| 1 | youtube_seo_audit | youtube | `youtube_seo_audit(video_id=VID)` → {score, issues} |
| 2 | get_video_seo_score | youtube-seo | `get_video_seo_score(VIDEO_ID)` → {score, issues[]} |
| 3 | get_video_details | youtube-seo | `get_video_details(VIDEO_ID)` → {title, description, tags, views} |
| 4 | Fix if score <70 | OpenCode LLM | Revise title/desc/tags → re-audit (max 2 cycles) |

## RULE: Clips enter Stage 8 ONLY after Stage 7 upload returned a video_id and Stage 6 metadata is final.

═══════════════════════════════════════════════════════════
STAGE 9: REPORT
═══════════════════════════════════════════════════════════

| # | Phase | Command |
|---|-------|---------|
| 1 | Backup A | `Copy-Item "D:\youtube system\output\final clips\[category]\[lang]\[Title]\clips\*.mp4" → "D:\youtube\_Projects\YouTube Shorts\"` ⚠ PENDING: `D:\youtube` husk is slated for deletion — confirm replacement destination with user before Phase A backup |
| 2 | Backup B | `Copy-Item "D:\youtube system\output\final clips\[category]\[lang]\[Title]\clips\*.mp4" → "Q:\_youtube\_Backup\final clips\[Title]\"` |
| 3 | Report | Print: clip # | duration | size | SEO score | video_id | url |

---

## TOOL INVENTORY (per video, ~17 clips)

| Tool | Calls | Stage |
|------|-------|-------|
| yt-dlp | 2 | 1 |
| ffprobe (QC: streams/format) | 17 | 5 |
| ffmpeg (YAVG + ebur128) | 17×2 = 34 | 5 |
| ffmpeg (ONE encode) | 17 | 4 |
| face_track_analyze.py | 17 (per clip) | 4 |
| gen_ass.py | 17 (per clip) | 4 |
| youtube MCP (youtube_upload, youtube_seo_audit) | 17×2 = 34 | 7, 8 |
| youtube-seo MCP (get_video_seo_score, get_video_details) | 17-34 | 8 |
| **MCP total** | **~51-68 calls/video** (kinocut removed = ~187 calls/video saved) | — |

## KINOCUT MCP — REMOVED

- `analyze_source`, `generate_clip`, `create_thumbnail` — GONE. ffmpeg + ffprobe replace all 3.
- `still_gate` — GONE (no thumbnails at all in this pipeline).
- The `youtube` MCP still exposes `youtube_set_thumbnail` / `youtube_ab_start` / `youtube_ab_rotate` — **NOT USED here**: uploads ship without a custom thumbnail (YouTube auto-picks a frame). Only at Stage 7 (upload) if the user explicitly asks.
- The `youtube-seo` `analyze_thumbnail` tool works on whatever frame YouTube auto-selected — informational only.

═══════════════════════════════════════════════════════════
TOKEN SAVING RULES
═══════════════════════════════════════════════════════════

1. Do NOT re-read SKILL.md mid-pipeline. Read ONCE at start.
2. Do NOT hunt for other tools. Use THIS file as the routing table.
3. Do NOT explain what you're about to do. Just do it.
4. Do NOT ask user for confirmation at every step. Only at Stage 7 (upload).
5. Do NOT retry failed commands more than once.
6. Do NOT generate alternative approaches. Follow this table exactly.
7. Progress report: one line per stage, not per tool call.
