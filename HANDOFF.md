# HANDOFF — YouTube Shorts Pipeline (read this first)

Last updated: 2026-09-28 · session ses_f3c0652bcffd7rEN8DorjJbfJO
Project root: `D:\youtube system` · rules: `system\rules.md` + `AGENTS.md`

## 1. Goal
Produce ~45 new shorts (bunker 15, mansion EN 15, mansion HI 15, bn0, stranded, g3 …),
QC-passed, metadata-written — and STOP. **NEVER upload without explicit user pass**
(`youtube_upload` signature must stay unchanged). Temp cleanup + `final_lock.ps1` only AFTER upload.

## 2. Contracts (violating these = rework)
- **Overlay graph (encode_stage4.py), exactly 4 inputs:** `[0]=src [1]=PILL(hook_pill.png) [2]=LCS(like-comment-subscribe.mp4) [3]=CS(center-subscribe.mov)`.
  - hook `overlay=0:84 enable between(t,1,15)`, fades 0.5s (pill canvas, drawtext `temp\hookNN.txt`, Montserrat 40)
  - LCS `x=268 y=56 enable gte(t,25)` (2026-09-28 corrected: content centered at (540,192)) — full 5s asset plays 25→30 and auto-vanishes (NO freeze)
  - CS (2026-09-29: +20% size per user): `scale=991:-2` → `loop=-1:size=1:start=296` → `scale=w='max(2,991*K)':h=-2:eval=frame`, `K=min(min(max((t-60)/0.3,0),1),1-min(max((t-69)/0.3,0),1))`; overlay `x='44.5+495.5*(1-K)' y='534.6+279*(1-K)' enable between(t,60,69.4)` — bounce in 60→60.3, out 69→69.3, GONE after (no hold-to-end). Traps: scale needs eval=frame (t rejected in init mode); w=0 = "input width" → clamp≥2; NO setpts+60 (loop pts = clip clock; overlay pairs by pts)
  - **notification-bell + youtube-subscribe permanently REMOVED — never re-add** (line 21 comment)
  - layers 20:45:35 blur-bed stack; face-zoom via `trackNN.json enable_expr`
- **Mediapipe:** old BlazeFace `FaceDetector` (`face_detector.tflite`) ONLY. Never FaceLandmarker/MODEL_LM/FACE_TRACK_ENGINE (the `face_landmarker.task` file on disk is unused).
- **Subtitles:** ALWAYS English (even `hi` sources). v2.3 ass burned via `[vbase]ass='{nn}.ass'` before overlays. Prep gate = `prep done, fails=0`.
- **Hooks:** ≤8 words, ALL CAPS, unique, clip01 = title; profile `hooks` dict → `temp\hookNN.txt`.
- **Stage 5 QC (qc_stage5):** 65–120s, 1080x1920 h264, 30000/1001, aac 48k, 2 streams, size<2GB,
  last-frame YAVG 14.5–22 converging to black, LUFS −14 ±0.6. Fail loop:
  `measure_loudness.py <profile> NN` → profile `measured` → delete `encNN.ok` → re-encode → re-QC.
- **Stage 6 SEO:** title ≤100 chars + ≥1 ALL-CAPS word(>2); desc exactly 3 lines; line3 = 3–5 hashtags incl `#Shorts`; tags 10–15, `", ".join(tags)` ≤470.
- **Runtime:** GPU cap 2 concurrent encodes; ONE source occupies `output\temp` at a time
  (never prep source B while A encodes — shared `hookNN.txt`/`NN.ass`); `-free` models only.

## 3. THE PROBLEM (why bunker must be re-rendered)
A SECOND project — `D:\youtube system\funclip-overlay` — is an AI loop (Antigravity session,
`autonomous-loop.sh` → `opencode run --auto`, spawned ~2026-09-27 13:12, has AUTO-RELAUNCH triggers):
- `_system.sh stage` copies NEW pool videos → `clips/sys_<md5>.mp4`
- `scripts/apply_overlay.sh` burns the OLD banned spec (hook.png y80 / like y152 gte25→END /
  **bell y32 gte40→END / subscribe y264 gte60→END**, FunClip x264, no end-fade)
- `_system.sh deliver` **copies results BACK OVER the originals** in `output\final clips\**`
  (weak gate: 1080x1920+audio+size>10KB+dur±0.5 only)

**Damage (verified 2026-09-28 12:41):**
- ALL 15 bunker clips in `output\final clips\extreme\en\Nuclear Bunker\clips\` = foreign
  23–34MB versions (mine were 105–134MB; overwritten 09-27 16:30 [clip01] + 09-28 08:20–09:58 [02–15]).
- 11 foreign files in `...\Last To Leave Mansion, Keeps It\clips\` (24–33MB, 16:23–16:30 09-27) —
  resurrected yesterday's deleted outputs; 05/06/09/10 absent. My pipeline never encoded mansion.
- Loop was KILLED by previous session (state backed up: `funclip-overlay\staging.map.bak`,
  `system_manifest.list.bak`; `staging.map` truncated to 0) but **RELIVED** (10 procs incl. new agent).
- Legacy 58 videos = CLEAN (all >60MB; QC 58/58 valid).

**Recovery (bunker — all prep intact):**
1. Kill loop again (match cmdline `autonomous-loop|apply_overlay`, walk descendant subtree, Stop-Process).
   Defense-in-depth: `bash _system.sh init` (use `C:\Program Files\Git\usr\bin\bash.exe` with
   `PATH=/usr/bin:/bin` exported — bare `bash` breaks) reseeds manifest = pool marked never-touch;
   keep `staging.map` empty (deliver then has nothing to push). Tell user to disable the auto-trigger at source.
2. Quarantine 11 mansion foreign files (move, don't hard-delete — "check first" rule).
3. Rebuild bunker: markers `output\temp\encNN.ok` — delete ALL 15 + delete the 15 mp4s, then
   `cd "D:\youtube system\output\temp"` → `python -X utf8 encode_stage4.py "..\..\system\profiles\bunker.json"`
   (bg, timeout 0; ~4.5 min/pair ≈ 35 min). Then `qc_stage5.py profiles\bunker.json` → loudness loop → 15/15.

## 4. Current pipeline state
- **bunker**: profile ✅ src = `...[_AbFXuGDRTs].h264.mp4` (AV1 problem SOLVED: dav1d full-build 7.1.1
  transcode → h264_nvenc intermediate; backup `bunker.json.av1.bak`), prep ✅ (15 pairs incl. repaired
  clip08, 15 ass, 15 hooks), encode ❌ (files contaminated → step 3 above), QC pending.
- **mansion EN**: profile ✅ (tag "Last To Leave Mansion"), face pairs ✅ (30 kept), prep not run
  (folder currently polluted by foreign files — quarantine first).
- **mansion_hi / bn0**: profiles ✅, queued.
- **stranded**: profile ✅ freshly built (`system\profiles\stranded.json`, self-check OK), moment/scene data ✅.
- **g3**: H.264 intermediate ✅ (`I Survived The Most Extreme Places On Earth [gTKS8SAwUzE].h264.mp4`,
  11.5GB) + `scenes_g3.txt` + `moments_g3.json` ✅ — **profile ✅ authored 2026-09-29** via
  `system\build_g3_profile.py` → `system\profiles\g3.json` (self-check OK: 15 hooks/slugs/meta,
  title lens 41–58, tag "I Survived Extreme Places v2", base `...\I Survived Extreme Places\v2`,
  measured {}). route.json ✅ (watch?v=gTKS8SAwUzE, @MrBeast) + SEO 15/15 PASS + **prep ✅ 2026-09-29 (15/15 v2 face pairs, 15 ass, 15 hooks, fails=0)** — encode-ready when the pause lifts.
- **58 legacy videos**: EN 43 (underground 13 + stranded 16 + survived 14) + hi grocery 15 — QC 58/58, metadata 58/58, captions v2.3. DO NOT TOUCH.
- Repo = clean-start commit `7e44388` (history wiped 2026-09-29; main only). Today's overlay +20% edits (`encode_stage4.py`, `test_build_fc.py`, spec docs) are UNCOMMITTED — user said wait for "say the word".
- **Stage 6/7 + runner built 2026-09-29**: `run_pipeline.py` (prep→encode→qc→seo→thumb→[--upload], exit codes 1-5/6), `run_all.bat` (loop-kill guard; default bunker+mansion; `upload` flag = `--upload`), `seo_stage6.py` (per-channel `base\seo\<ch_id>\NN.json`, Stage-6 contract enforced, one MCP `get_tag_analysis` enrichment, graceful fallback), `upload_stage7.py` (whoami → upload PRIVATE → playlist cached in route.json → `youtube_seo_audit` → appends `system\post_queue.json`), `poster.py` (schedule day/time + max_per_day, one publish/channel/run via `youtube_update_metadata(privacy=public)`), support libs `mcp_client.py` (stdio MCP to the local youtube/youtube-seo servers) + `routing.py` (route.json/channels.json loader). Smokes: SEO 15/15 bunker ✅, MCP transport ✅, poster empty ✅, usage ✅ — upload/publish NOT run (upload pass pending). **YouTube OAuth token EXPIRED/REVOKED** → re-auth `system\youtube-mcp-server\authorize.py` BEFORE Phase 6/7. route.json exists for all three routed projects (bunker ✅, mansion ✅, g3 ✅) — seo_stage6 PASS 15/15 each.
- **Overlay loop killed at source 2026-09-29**: scheduled task `funclip-overlay-loop` DISABLED (was every 30 min + logon → run-loop.ps1), staging.map 0 B, manifest 73, zero loop processes. `Start-AntigravityBot.vbs` left alone (unrelated Telegram bot).

## 5. Space audit findings (user asked; NOTHING deleted)
- Outside protected `output\4k video` (26.4GB) + `output\final clips` (8.7GB): 3.56GB total.
- `output\temp` 2.03GB (proxies_g3 ~1.1GB superseded, loud_fix_backup 0.73GB obsolete, logs 2MB) → post-upload candidates.
- `.git` = 1.19GiB: 624 loose objects, ALL reachable — `temp/proxies_g3/*.mp4` (~1.16GB) committed in
  old snapshots + pushed to GitHub remote. `git gc` reclaims ~nothing; only history rewrite (~→80MB) — destructive, needs user approval.
- No byte-duplicates anywhere except funclip-overlay's staged copies (0.8GB, part of the loop problem).

## 6. Pending user decisions (do NOT assume)
1. Upload: branding? explicit pass? scope (58 legacy or 43 EN)? titles policy?
2. "Fully functional" definition (user's checklist unanswered).
3. Commit authorization ("say the word").
4. Whether funclip-overlay loop should EVER run again (it conflicts with the bell/YS ban).
5. `.git` history rewrite approval.

## 7. Quick reference
- Profiles: `system\profiles\{bunker,mansion,mansion_hi,bn0,stranded,g3}.json`
- Stages: `prep_stage4 → encode_stage4 → qc_stage5 → seo_stage6 → thumb_gen → [upload_stage7]` orchestrated by `run_pipeline.py` (all take `<profile.json> [NN…]`); `poster.py` publishes queued uploads; legacy `meta_stage6.py` still writes `metadata\NN.txt`. Upload gate: `--upload` + explicit user pass.
- Intermediates: `output\4k video\en\*.h264.mp4` (g3, bunker). AV1 sources NEVER touch cv2 directly.
- Encode cwd MUST be `output\temp`. Foreground `ffmpeg` = FunClip build; bg shells resolve WinGet 7.1.1 (both fine for h264).
- QC/CS sanity probe (991 size, 2026-09-29): red bbox x[178..901] y[716..915] (724×200 incl. chroma bleed, center (539,815)) at t 60.3–69; true content 614×172 ≈ x235 y731; NOTHING ≥69.4 (2px clamp only); end frames Y≈16.
