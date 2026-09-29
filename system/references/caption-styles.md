# Caption Styles — EXACT ASS Specs for YouTube Shorts (v2.3)

> v2.3 = **Montserrat Bold 96px MIXED CASE**, `\fsp-0.5` tracking, absolute per-line
> `\an8\pos`, `ACTIVE_RISE` pop compensation — geometry still matched to the reference
> frame `v2_hook.png` (tops 1321 / 1394 / 1464, pitch 71.5, cap 43).
> **v2.3 changes (user 2026-09-26)**: MIXED CASE (reference subs contain lowercase —
> v2.2's `.upper()` removed) and tracking `0 to −0.5px` (`\fsp-0.5` → `\fsp-0.5`).
> The user's "38–44px" size spec = visible cap height, NOT em — em stays **96px**
> (confirmed: renders 43px caps ≈ 4% of 1080; Montserrat cap ≈ 0.448 × fontsize).
> The old **Anton 68px / MarginV=400 / WIDTH=34** spec is DEAD — do not use it.

## Language policy (user decision 2026-09-26)
- **ALWAYS English captions** — for every upload, both `en` and `hi` videos. English
  transcript + this v2.3 spec. No Devanagari/Hindi caption rendering ever.
- The **Hi Devanagari font polish task is REMOVED** (user: "remove it") — do not
  propose, plan, or do Hindi-caption work.

## Font
- **Captions family**: Montserrat Bold (Google Font) — `temp\fonts\montserrat-bold.ttf`
  (reference frame visually confirmed as Montserrat Bold)
- **Fallback**: Arial Black (if Montserrat unavailable)
- **Size**: 96px (PlayResY=1920, so fontsize units = pixels; renders cap height
  **43px** = 0.448 × 96 — matches ref cap 43)
- **Case**: MIXED CASE (v2.3 — transcript's own casing rendered as-is; gen_ass.py
  does NOT `.upper()`. Hook banner / Hook Title Rule stays ALL CAPS — that's the
  separate drawtext pill, not a caption)
- **Outline**: 4px solid black (#000000)
- **Shadow**: 3px offset, 50% opacity black
- **Tracking**: `{\fsp-0.5}` per-line override (v2.3 user spec: "0 to −0.5px /
  −1% to 0%" — normal to slightly tight). Replaces v2.2's `\fsp-0.5`, which was
  measured from the caps-only reference (585 vs 642 ink px). MUST be the
  override: libass **ignores negative style-field `Spacing`** (positive values
  work, negatives do not).
- **Hook banner family**: Montserrat Bold 40px — `temp\fonts\montserrat-bold.ttf`
  (drawtext, NOT an ASS event)

## Colors
| Element | Hex | BGR (`&H...`) |
|---------|-----|---------------|
| Active word (being spoken) | `#FFE500` (canary yellow) | `&H0000E5FF` |
| Inactive word | `#FFFFFF` (white) | `&H00FFFFFF` |
| Outline | `#000000` (black) | `&H00000000` |
| Hook text | `#000000` (black) | — |
| Hook box | white @ 0.92 opacity | — |

- **Active word = current word being spoken** → yellow + **10% pop** (scale 100→110 over 0.1s via `\t(0,10,\fscx110\fscy110)`)
- **Inactive words = all other words** → white, scale 100
- Word-level timing: each caption unit is split into per-word Dialogue events; boundaries formatted once and shared (contiguous, zero gap between words)

## Position — ABSOLUTE per-line (NOT MarginV)
Each visual line is its **own Dialogue** with `{\an8\pos(540,y)\fsp-0.5}` — the style's
Alignment/MarginV fields are always overridden (kept only for compatibility).
Geometry constants (gen_ass.py):

| Constant | Value | Meaning |
|----------|-------|---------|
| `LINE_PITCH` | 71.5 | ref ink tops 1321 / 1394 / 1464 → 71.5 avg |
| `LAST_INK_TOP` | 1464 | bottom-line ink top (ref L3: 1464..1506) |
| `BOX_DELTA` | 25 | `\an8` box top → ink top at 96px (position-independent) |
| `ACTIVE_RISE` | 6.82 | pop compensation (see Animation) |
| `TRACKING` | −0.5 | `{\fsp-0.5}` (see Font) |
| `CX` | 540 | centered (ref cx=539) |

- **y formula**: `y = LAST_INK_TOP − (nlines−1−i) × 71.5 − 25`
  → 1-line y=1439 · 2-line y=1367.5 / 1439 · 3-line y=1296 / 1367.5 / 1439
  (i = line index, 0 = top). Popped lines: `y − 6.82`.
- All ink (max 3 lines: y 1296 box → ink 1321, bottom cap 1506) sits inside the
  **bottom blur zone** (starts y=1248 under the 20/45/35 layout) — never on the
  hero band (ends y=1248). Uniform in BOTH modes — position never jumps between
  wide and close-up segments.
- **Hook banner**: pre-rendered pill PNG `assets\hook_pill.png` (1080×120, radius 50, white α235)
  — pill input is looped (`-framerate 30 -loop 1 -t $DUR`), drawtext runs ON the pill canvas with
  `x='(W-text_w)/2':y='(H-text_h)/2'` (text centered on the pill), then the group is overlaid at
  `0:84` (fully inside the 384px top blur zone), window `enable='between(t,1,15)'` with 0.5s alpha fade-in at
  t=1 and fade-out at 14.5 — **t=1–15 (Top Overlay Timeline, rules.md — FIXED)**.
  **Text UNIQUE per clip**: max 8 words, ALL CAPS, that segment's most shocking line — main video title on
  clip 01 only (full rule: prompt.md `Hook Title Rule`)

## Animation
- **Active word pop**: scale 100→110 in 0.1s (`\t(0,10,\fscx110\fscy110)`), then reset to 100 when word goes inactive
- **`ACTIVE_RISE` = 6.82**: `\fscy110` inflates the line's ascent by 10%
  (0.1 × 0.7100 × 96 = 6.82 → baseline drops, cap top +7). Popped lines are
  shifted up by this so every line's normal caps stay on the pitch grid
  (ref L2: pop sticks up ~4px WITHOUT moving the line). Verified in demo:
  active line ink top lands 1465 vs ref 1464.
- **Fade-in**: 0.5s at clip start (`fade=t=in:st=0:d=0.5`, `afade=t=in:st=0:d=0.5`)
- **Fade-out**: video `fade=t=out:st=($DUR-1):d=1`; audio `afade=t=out:st=($DUR-0.5):d=0.5`
  (PowerShell needs `${vfade}`/`${afade}` braces — bare `$vfade:d` interpolates empty)
  **Black = YAVG 16**, not 0 (limited-range yuv420p). Fade QC against 16.
- **Hook banner**: pill + text fade in 0.5s at t=1 and fade out 0.5s at t=14.5
  (`fade=t=in:st=1:d=0.5:alpha=1,fade=t=out:st=14.5:d=0.5:alpha=1` on the pill canvas),
  visible t=1–15 (`overlay=0:84:enable='between(t,1,15)'`), then removed.
  Text goes through `drawtext:...:textfile=` — never `text=`, which breaks on `$` and `,`.

## Timing / Wrapping
- **Max chars per rendered line**: 16 (`WIDTH` — ref wrap "AND WE'RE GONNA" = 15 chars)
- **Max lines**: 3
- **Max chars/caption unit**: 48 (`CHUNK` — ≤3 rendered lines, ref shows 3)
- **Word boundaries**: proportional to char length within caption unit (no word-level timestamps in source)

## ASS Template (exact)
```
[Script Info]
Title: YouTube Shorts Caption Style v2.3
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: MainCaption,Montserrat,96,&H00FFFFFF,&H0000E5FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,3,2,20,20,400,1
Style: HookBanner,Montserrat,40,&H00000000,&H00FFFFFF,&H00FFFFFF,&H80000000,-1,0,0,0,100,100,0,0,3,0,0,8,20,20,240,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
```
> **PrimaryColour = white** (inactive default). Active word override inline:
> `{\c&H0000E5FF&\t(0,10,\fscx110\fscy110)}WORD{\fscx100\fscy100\c&H00FFFFFF&}`
>
> Style Alignment=2 / MarginV=400 are legacy — **every event carries
> `{\an8\pos(540,y)\fsp-0.5}` which overrides them**.
>
> HookBanner style stays defined for compatibility, but the hook banner is drawn by drawtext (Stage 4), NOT by an ASS event.

## Word-Level Event Example
Caption unit `"AND WE'RE GONNA BE RACING EACH OTHER IN"` (3 lines, active word
"RACING" on line 2) — one Dialogue per word, each containing ALL visual lines
at fixed `\pos` (so only the active word is yellow):
```
Dialogue: 0,0:00:00.00,0:00:00.52,MainCaption,,0,0,0,,{\an8\pos(540,1296)\fsp-0.5}AND WE'RE GONNA{\an8\pos(540,1360.68)\fsp-0.5}BE {\c&H0000E5FF&\t(0,10,\fscx110\fscy110)}RACING{\fscx100\fscy100\c&H00FFFFFF&} EACH{\an8\pos(540,1439)\fsp-0.5}OTHER IN
Dialogue: 0,0:00:00.52,0:00:01.04,MainCaption,,0,0,0,,{\an8\pos(540,1296)\fsp-0.5}AND WE'RE GONNA{\an8\pos(540,1367.5)\fsp-0.5}BE RACING EACH{\an8\pos(540,1439)\fsp-0.5}OTHER IN
```
(Line 2's y is 1360.68 = 1367.5 − 6.82 ONLY while its word is active — `ACTIVE_RISE`.)

## Generation Workflow
1. Read transcript: `D:\youtube system\output\transcript\en\plain.txt` (timestamped, `[HH:MM:SS,mmm] text` — ALWAYS `transcript\en\`, Captions Rule)
2. Run: `python D:\youtube system\system\gen_ass.py START_SEC END_SEC OUT.ass` (from project dir)
3. Output: `ass\NN.ass` (UTF-8 with BOM for VSFilter/libass compat)
4. ffmpeg Stage 4 burns: `ass='NN.ass':fontsdir='fonts'` (relative path, run from `temp\`)

## Verification
- Reference frame: `C:\Users\bhavesh jeengar\AppData\Local\Temp\topov\v2_hook.png`
  — L1 ink 1321..1363 cap43 · L2 normal top 1394 (popped band 1390, cap47) ·
  L3 1464..1506 cap43 · pitch 71.5 · active ≈#FFE500 · widths 585/544/282.
- Geometry check tool: `output\temp\verify_subs.py` (measures rendered demo frames
  against those targets). Same-text side-by-side: `output\temp\ref_text_test.py`
  → `output\temp\sub_compare2.png`.
- libass gotchas: negative style `Spacing` ignored (use `{\fsp}` override); `\t`
  un-progressed at event t=0 (extract frames mid-event / decoded-seek); yellow
  `&H0000E5FF` invisible to white-only ink thresholds.
