# YouTube Shorts Pipeline — Run Prompt

## Trigger
Type: "youtube system"

## Response Flow

When user types "youtube system", respond:

"Hello Sir! What would you like to do?

1. **YouTube Link** — I will download the video + subtitles and run the full pipeline
2. **Personal File** — Provide your video path (and SRT path if available), I will skip download and run the pipeline directly"

Wait for user choice.

---

## Option 1: YouTube Link

User provides: YouTube URL

Run the full pipeline:

1. Download
   - yt-dlp: best 4K video → D:\youtube system\output\4k video\en\ (HI: 4k video\hi\ — `-f "bv*+ba[language=en]"` / `[language=hi]`)
   - yt-dlp: --write-subs --sub-lang en --convert-subs srt → D:\youtube system\output\transcript\en\ (HI SRT → transcript\hi\; captions ALWAYS read en\)
   - Skip if files already exist

2. Analyze
   - kinocut: video_info (codec, fps, resolution, duration)
   - kinocut: scene_detect (find natural boundaries)
   - kinocut: waveform (identify silence gaps)

3. Select clips
   - Read full SRT transcript
   - Pick 15-18 viral moments (75-85s each)
   - Snap cuts to scene boundaries
   - Exclude sponsor segments
   - Strong hook in first 3 seconds
   - Spread evenly across full duration

4. Per clip (x17):
   - Determine crop from source resolution (ffprobe):
     • 16:9 → crop=ih*9/16:ih:(iw-ih*9/16)/2:0
     • 9:16 → no crop
     • 1:1 → crop center + blurred pad to 9:16
   - scale=1080:1920:flags=lanczos
   - Generate word-by-word ASS (ALWAYS English, Montserrat Bold 96px, yellow active +10% pop, white inactive, per-line \an8\pos + \fsp-0.5 — SAME ASS for EN and HI; never Mangal, never Hindi ASS)
   - Burn ASS
   - color_grade: subtle warm cinematic LUT (same for all clips)
   - silence_removal: tighten dead air >1s
   - loudnorm=I=-14:TP=-1.5:LRA=11
   - Video fade in 0.5s / out 1.5s (fade=t=in:st=0:d=0.5, fade=t=out:st=($DUR-1.5):d=1.5)
   - Audio fade in 0.5s / out 1s (afade=t=in:st=0:d=0.5, afade=t=out:st=($DUR-1):d=1)
   - Export: libx264 CRF 16 preset slow, AAC 192k 48kHz, +faststart, yuv420p

5. Per clip — Quality Gate:
   - release_checkpoint: verify 1080x1920, H.264, AAC, 75-85s, audio present
   - If FAIL → video_rescue

6. Metadata (per clip):
   - Title: SEO, max 100 chars, hook + emotion
   - Description: 2-3 lines + #Shorts + 3-5 hashtags
   - Tags: 10-15 (broad + specific)
   - Save to metadata\NN.txt

7. SEO Check:
   - youtube-seo: get_video_seo_score on each clip
   - If score <70: revise title/desc/tags, re-score

8. Upload:
   - youtube: upload all clips as Shorts (private)
   - youtube: seo_audit on each
   - No custom thumbnails (pipeline ships without thumbnails)

9. Output:
    - Create upload_sheet.txt
    - Print summary: # | Start | End | Duration | Hook | Size | SEO Score

10. Cleanup:
    - Delete temp files
    - Delete empty folders
    - Keep: ass/, clips/, metadata/, upload_sheet.txt

---

## Option 2: Personal File

User provides:
- Video path: (e.g., D:\Videos\my_video.mp4)
- SRT path: (optional, if available)

Run the pipeline from Step 2 onwards (SKIP Step 1 entirely):

- Do NOT download anything
- Do NOT use yt-dlp
- Use the provided video path as source
- If SRT provided: use it directly
- If SRT NOT provided: ask "Do you have an SRT file for this video? If not, I will use FunClip to transcribe."
- Then continue: Step 2 (Analyze) → Step 3 (Select) → ... → Step 10 (Cleanup)

Output goes to:
D:\youtube system\output\final clips\[category]\[lang]\[Video Filename without extension]\

---

## Folder rules
- D:\youtube system\output\4k video\en\       (Option 1 only — source; hi\ for HI audio)
- D:\youtube system\output\transcript\en\     (Option 1 only — SRT; captions ALWAYS read en\)
- D:\youtube system\output\face_track\en\     (cropNN.txt / trackNN.json, prefixed per video)
- D:\youtube system\output\temp\             (ffmpeg working dir + fonts\)
- D:\youtube system\output\final clips\[category]\[lang]\[Title]\clips\
- D:\youtube system\output\final clips\[category]\[lang]\[Title]\ass\
- D:\youtube system\output\final clips\[category]\[lang]\[Title]\metadata\
- D:\youtube system\output\final clips\[category]\[lang]\[Title]\upload_sheet.txt
- Inputs NEVER live inside final clips\ — outputs NEVER live outside it
- [category] = extreme | funny | podcast | kids | movies | facts | motivation  ·  [lang] = en | hi
- Create folders only when files go in them

## Naming
- Clips: NN_short-slug.mp4
- Metadata: NN.txt
