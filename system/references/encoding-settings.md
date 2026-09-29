# Encoding Settings Reference

## FFmpeg Flags (H.264)
```
-c:v libx264 -crf 18 -preset ultrafast -pix_fmt yuv420p
-c:a aac -b:a 192k -ar 48000
-movflags +faststart
```
`ultrafast` = one-pass requirement (a 78s clip encodes in well under a minute).

## Crop Formulas

### 16:9 → 9:16
```
crop=ih*9/16:ih:(iw-ih*9/16)/2:0
```
Example: 1920x1080 → crop width = 1080*9/16 = 607.5 → center: (1920-607.5)/2 = 656.25

### 4:3 → 9:16
```
crop=ih*9/16:ih:(iw-ih*9/16)/2:0
```
Same formula works for wider sources.

### 1:1 → 9:16
```
crop=ih:ih:0:0,pad=1080:1920:(1080-ih)/2:0:color=black
```

### Already 9:16
```
scale=1080:1920:flags=lanczos
```

## Resize (Lanczos)
```
scale=1080:1920:flags=lanczos
```

## Audio Normalization (EBU R128)
```
loudnorm=I=-14:TP=-1:LRA=11
```

## Video Fade (variable $DUR)
```
fade=t=in:st=0:d=0.5,fade=t=out:st=($DUR-1.5):d=1.5
```

## Audio Fade (variable $DUR)
```
afade=t=in:st=0:d=0.5,afade=t=out:st=($DUR-1):d=1
```
Compute once and brace the name — see the PowerShell trap below:
```powershell
$vfade = [math]::Round($DUR - 1.5, 3)  # 78.55 -> 77.05
$afade = [math]::Round($DUR - 1, 3)    # 78.55 -> 77.55
# fade=t=out:st=${vfade}:d=1   /   afade=t=out:st=${afade}:d=0.5
```

**VERIFY the fade landed**: `ffmpeg -i OUT -vf "select='gte(t,$DUR-1.2)',signalstats,metadata=print:key=lavfi.signalstats.YAVG" -f null -`
must decline monotonically to **YAVG ≈ 16 = pure black in limited-range yuv420p** (Y=16 is black, NOT a bug). Always scan with a FULL decode using true frame timestamps — `-ss`-relative scans give ambiguous `pts_time`.

## Mode B — Blurred Background (DEFAULT: MrBeast/extreme/vlog)
```
[0:v]split[bg][fg];
[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.25[bg2];
[fg]scale=1080:864:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:864[fg2];
[bg2][fg2]overlay=0:384,ass='NN.ass',...
```
Any source ratio → always lands 9:16 (1080x1920).

**Three-zone layout (asymmetric, Mode B):**

| Zone | Height | % | Content |
|------|--------|---|---------|
| Top blur | 0–384 | 20% | gblur σ40 + brightness −0.25; hook pill lives here (y=84) |
| **Hero band** | 384–1248 | 45% | Main video, **fill-crop to 1080×864**, full-bleed sharp |
| Bottom blur | 1248–1920 | 35% | Same blur as top; **subtitles live here (per-line `\an8\pos` — ink 1296..1506, max 3 lines)** |

fg is `force_original_aspect_ratio=increase` + `crop=1080:864` — it covers the band edge-to-edge (sides get center-cropped away), so `overlay=0:384` and there are **no side-blur slivers**. The old `scale=iw*1.05:ih*1.05` nudge is gone — the 864px fill-crop IS the enlargement (was 608→864, +42%).
Subtitle math: captions are absolutely positioned per line (`{\an8\pos(540,y)}`) — bottom-line ink top 1464, cap bottom `1506 > 1248` (band bottom); top-most 3-line ink top 1321 > 1248 → ALL subtitle ink sits in the bottom blur zone, NOT on the main video.

## Mode A — Face-track Crop (podcast/interview, single person)
```
[v0]crop=608:1080:x='<EXPR>':y=0,scale=1080:1920:flags=lanczos[fa]
```
608:1080 = 9:16 slice of 1920x1080 (4K source → `scale=1920:1080,` first).

**MUST use named crop args: `x='...':y=0`.** ffmpeg 9.0.1 rejects a bare positional after a named arg — `crop=608:1080:'EXPR':0` fails with `Failed to configure input pad`. The crop filter has **no `eval` option**, so the expression is evaluated per-frame regardless.

Expression = smoothed crop-x written by `face_track_analyze.py <DUR>` to `output\face_track\en\<prefix>_crop_test.txt` (+ `<prefix>_track.json` holds the `enable_expr` close-up ranges; JSON also records `engine` = `mediapipe-1.0.1-landmarker` / `-detector`). `<prefix>` = video folder name — `face_track\<lang>\` is one shared flat folder per language (default `en\`), so every file is prefixed (never a bare `crop_test.txt`).

### ⚠ Expression nesting depth cap = 98
ffmpeg 9.0.1 silently refuses any expression nested deeper than **98** (99 → `-22`, `Failed to configure input pad on Parsed_crop_N`). Empirically binary-searched: depth ≤98 OK, ≥99 fails.

A right-leaning `if()` chain over N control points has depth ≈ N×4, so a 78s clip (178 points ≈ depth 712) always blows the limit. `face_track_analyze.py` therefore emits a **balanced if-tree** (binary-search routing over the time axis → depth ≈ log2(N), measured **nesting 12**) and hard-exits if `expr_nesting > 120`. Keep that generator — do not hand-roll a chained expression.

Before a full encode, sanity-check any long expression cheaply:
```powershell
ffmpeg -y -f lavfi -i "color=c=red:s=1920x1080:r=30" -vf "crop=608:1080:x='$E':y=0" -frames:v 1 t.jpg
```

## Podcast variant (prepend to -af, before afade/loudnorm)
```
silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.5,afade=...,loudnorm=...
```

## Silence Removal (1.5s threshold)
```
silenceremove=start_periods=1:start_threshold=-40dB:start_duration=0.5:stop_periods=1:stop_threshold=-40dB:stop_duration=1.5
```

## Hook Banner — pill PNG (Step 2 asset)
`D:\youtube system\system\assets\hook_pill.png` — generated once by PIL: **1080×120, corner radius 50, white alpha 235**. Used as a SECOND input — looped for the whole clip, drawtext runs ON the pill canvas (text and pill then move/fade together):
```
pill input: -framerate 30 -loop 1 -t $DUR -i hook_pill.png
[1:v]format=rgba,drawtext=fontfile='fonts/montserrat-bold.ttf':textfile='hookNN.txt':
  fontcolor=black:fontsize=40:x='(W-text_w)/2':y='(H-text_h)/2':
  fade=t=in:st=1:d=0.5:alpha=1,fade=t=out:st=14.5:d=0.5:alpha=1[hook];
[sub][hook]overlay=0:84:enable='between(t,1,15)'[with_hook]
```
W/H are the **pill canvas (1080×120)** → drawtext is centered on the pill; the whole group lands at `y=84` → pill spans 84–204, fully inside the 384px top blur zone. Hook window = **1–15s**: 0.5s alpha fade-in at t=1, 0.5s fade-out at 14.5, then the overlay is removed (Top Overlay Timeline, rules.md — FIXED). Input `-t $DUR` bounds the looped pill. Text MUST go through `textfile=` — `$` and `,` break `drawtext=text=`.

## Overlays — NONE (CTA REMOVED)
No CTA and no overlays EXCEPT the Top Overlay Timeline (rules.md, STACKED — each enters then STAYS except where noted): hook 1–15 with fades, like-comment-subscribe 25→30 (full 5s asset plays, collapse-outro ends empty → auto-removed, NO freeze); plus the center-subscribe popup (main band, enters at 60 → bounces out 69→69.3 and is gone; the global end fade covers clip end). **notification-bell + youtube-subscribe REMOVED permanently (2026-09-26)** — they froze in place to clip end instead of exiting smoothly; never re-add. The graph has exactly **4 inputs**: 0 = source video, 1 = `hook_pill.png` (looped `-framerate 30 -loop 1 -t $DUR`), 2 = `overlays\like-comment-subscribe.mp4`, 3 = `overlays\center-subscribe.mov` — no others. LCS is NOT held (`format=rgba,setpts=PTS+25/TB` — stream ends at 30s, empty tail repeats invisibly). Center-subscribe IS held (loop): `scale=991:-2,loop=loop=-1:size=1:start=296,scale=w='max(2,991*K)':h=-2:eval=frame` + `enable='between(t,60,69.4)'` at x='44.5+495.5*(1-K)' y='534.6+279*(1-K)' — the loop makes its stream infinite → output MUST be bounded `-t $DUR`. No other overlays/effects ever (speed lines/confetti/arrows/particles/glitch/emoji/kinetic text/transitions). Old CTA assets deleted from the project — never re-add.

## Canonical one-pass graph (dual mode A+B, MrBeast/vlog)
```
split=3 → [fa] face-track crop 608:1080 x=..:y=0 → 1080:1920 lanczos
        → [fb] blurred fill   scale=increase,crop=1080:1920,gblur=40,eq=brightness=-0.25
        → [fg] hero band      scale=increase,crop=1080:864 (main video 45% full-bleed) → overlay=0:384
[wide][fa] overlay=0:0:enable='<close ranges>'      ← close-up pops over blurred wide bg
        → ass='NN.ass' → hook (1–15, drawtext on pill canvas + 0.5s alpha fades) → like-comment-subscribe (25→30, full 5s plays, auto-removed, x=268 y=56) → center-subscribe (60→69.4 K-bounce, scale=991 + K-scale eval=frame + loop-hold f296, x=44.5 y=534.6 MAIN band) → fades → `-t $DUR` [v]
audio → loudnorm=I=-14:TP=-1:LRA=11 → afades [a]
```
Close-ups are full-bleed, wide shots stay blurred-fill → **100% canvas coverage in every frame**.

## ffmpeg 9.0.1 + PowerShell traps (all hit during clip 01)
| Trap | Fix |
|------|-----|
| `-filter_complex_script` **removed** | pass `$fc` inline: `-filter_complex $fc` |
| `-vsync 0` **removed** (9.0.1) | `-fps_mode passthrough` (frame-select extraction) |
| `$vfade:d` parses as drive/scope-qualified var → renders empty → `st==1` | brace it: `st=${vfade}:d=1` (same for `${afade}`) |
| `crop=608:1080:'EXPR':0` | named args: `crop=608:1080:x='EXPR':y=0` |
| expression depth >98 | balanced if-tree (see Mode A above) |
| `python -c` strips inner quotes | always write a `.py` file |
| source filename contains `$` | single-quote paths; filter-internal paths stay cwd-relative (`cwd=temp`) |
| ffmpeg prints the whole graph before `Error : Invalid argument` | find the real token via `Error parsing a filter description around:` |
| drawtext `textfile` ending in **trailing CRLF** (`\r\n`) | renders **NO text at all, exit 0, silent** — write the file with NO trailing newline (`[IO.File]::WriteAllBytes`, ASCII). LF-only ending is OK. Diagnose with `YMIN` in the pill crop (text ⇒ YMIN<50; empty ⇒ YMIN≈235) |

## Overlay Files (permanent)
- Hook: D:\youtube system\system\assets\hook_pill.png (looped `-framerate 30 -loop 1 -t $DUR`)
- Like+Comment+Subscribe: D:\youtube system\system\assets\overlays\like-comment-subscribe.mp4 (5s file — freeze point **4.0s**)
- Center Subscribe: D:\youtube system\system\assets\overlays\center-subscribe.mov (PNG/RGBA **3840×2160, exactly 10.000s, clear background** — built-in bounce pop; tail f297-299 EMPTY so last visible = f296/t9.87; loop-held from 60 to clip end, removed by the global end fade)
- REMOVED permanently (2026-09-26): notification-bell.mov + youtube-subscribe.mp4 — they froze in place to clip end instead of exiting smoothly. Files may stay on disk; never wire them back into the graph.
- Positions (stacked Top Overlay Timeline — rules.md):
  - Hook: `x=0, y=84` (top blur, alone 1–15s)
  - Like+Comment+Subscribe: `x=268, y=56` (content centered at (540,192),
    middle of the 0–384 top-blur zone; old y=179 bottom-centered it —
    corrected by user 2026-09-28)
  - Center Subscribe: `x=44.5, y=534.6` (x/y re-anchor with K during the bounce) — full 4K frame scaled to 991 wide (canvas 991×558, **+20% per user 2026-09-29**; was 826/−15%) so visible content ≈614×172 sits at the MAIN band center (x=540, y=816); only overlay allowed in the main band, never in the top zone or subtitle zone
- Hold chains: Center-subscribe (window 60→69.4): `format=rgba,scale=991:-2,loop=loop=-1:size=1:start=296,scale=w='max(2,991*K)':h=-2:eval=frame` + `enable='between(t,60,69.4)'` — the loop repeats the last VISIBLE frame (f296) across the whole window (never hold true EOF; f297-299 are empty). LCS holds NOTHING: `format=rgba,setpts=PTS+25/TB` — full 5s plays 25→30, collapse-outro ends empty → auto-removed.
- Overlay audio: NEVER mapped (video streams only)
- Format: rgba (transparent)
