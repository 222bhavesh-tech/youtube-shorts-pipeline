# MUSCLE MEMORY — reflex routing + complete folder map + speed baseline

> **PROJECT: youtube-system · KEY PREFIX: `MM-YT-` · FILE: this one only.**
> One project = one file = one ID namespace. NEVER merge projects into a single file.
> Canonical file. Loaded by context-mode as source `Muscle memory: routing + folder map`.
> When this file is in the KB, the ecosystem answers WITHOUT reading anything else.
> Last measured: 2026-09-26.

## 1. REFLEX ROUTING (act first, think second)

| Stimulus | Reflex tool | Latency |
|---|---|---|
| "who calls X / where is Y / blast radius" | `trace_path` / `search_graph` / `detect_changes` | **30–50 ms** |
| "architecture, layers, hotspots, entry points" | `get_architecture(aspects=[...])` | **37 ms** |
| "what does the spec say / current value" | `ctx_search` with a **queries ARRAY** (one call) | **~64 ms/query** |
| "why did we decide / what was agreed" | `mem0.search_memories` FIRST | **~550 ms** |
| big data, multi-command, whole-tree analysis | `ctx_batch_execute` (auto-indexes, 4–8 concurrency) | one round trip |
| literal text, .ps1 internals, non-code | grep / `ctx_execute` | n/a |

**Hard rules (muscle memory):**
1. Graph first, context second, mem0 third, files NEVER as first resort.
2. Flood guard: never fire rapid individual search calls — batch into one `ctx_search` array or one `ctx_batch_execute`. Batching is also the FASTEST pattern (9 queries / 335 ms in one burst).
3. mem0 writes return `PENDING` → verify via `get_event_status` until `SUCCEEDED`; silent failures happen.
4. Re-run `index_repository` after bulk code changes; `ctx_purge(scope:"project")` only when a spec revision makes old KB content wrong.
5. Only `-free` models; max 2 concurrent ffmpeg encodes.

## 2. EVERY FOLDER (complete inventory — 5 top-level, 46 subdirs)

| Folder | Files | Size | Contents / indexed source |
|---|---|---|---|
| `output` | 827 | 18,291 MB | everything produced (see breakdown) |
| ├ `4k video` | 7 | 8,025 MB | user-downloaded sources — **KEEP**: `en` 5 files/5,826 MB, `hi` 2/2,200 MB (pure mp4, no text → tree-covered only) |
| ├ `face_track` | 116 | — | `en` 86 + `hi` 30 JSON/text per-clip track data (indexed) |
| ├ `final clips` | 178 | — | `extreme/en` 132, `extreme/hi` 46; **empty stubs: facts, funny, kids, motivation, movies, podcast (0 files)** |
| ├ `temp` | 507 | 2,078 MB | working artifacts — 190 text files (transcripts/ass/logs, first 100 indexed) + `fonts/` holds `montserrat-bold.ttf` |
| └ `transcript` | 15 | — | plain.txt + timing per source (indexed) |
| `system` | 104 | 83 MB | pipeline code + 38 text files; 16 spec docs indexed; `assets` 6 files/60 MB (hook_pill.png etc.) |
| `funclip-overlay` | 19 | ~0 | overlay builders + 65/65 test suites (`clips`,`final`,`overlay`,`scripts`) — 76 sections indexed |
| `overlay` | 4 | ~0 | binary overlay assets (dir-tree covered) |
| `.opencode` | 3,672 | 53 MB | app runtime (js/ts/map skipped; 2 config json/md indexed) |
| `.git` | 4629 | — | excluded everywhere by design |

**Extension histogram (domain shape):** .ts 1587, .js 877 (runtime) → then **.txt 249, .json 111, .mp4 85, .ass 85, .png 65, .py 58, .md 50, .log 45, .ps1 27**.
**Text concentration:** `output/temp` 190 → `face_track/en` 86 → `system` 38 → `face_track/hi` 30 → per-clip `ass`/`metadata` 13–16 each.

## 3. SPEED BASELINE (measured 2026-09-26)

| Operation | ms |
|---|---|
| `query_graph` Cypher | 29 |
| `get_architecture` | 37 |
| `trace_path` | 40 |
| `search_graph` | ~50 |
| `ctx_search` per query | 61–69 (avg 64) |
| 9-query mixed parallel burst (ctx + graph) | **335 total** |
| mem0 semantic search | 518–620 (parallel → ~260 each) |
| index 4 folders / 124 files (one-time) | 2,476 |

**Interpretation:** every orientation question resolves in 30–65 ms from memory vs 1–3 s per file read.
Graph ≈ 5× faster than ctx ≈ 18× faster than mem0 — but each store owns its layer (structure / docs / decisions).

## 4. AUTO-SAVE PROTOCOL — COMPACTION ONLY (three-store write)

**Trigger — ONLY at compaction / end-of-task points. NOT after every event.**
*(user decision 2026-09-26 — revised from "always on")*

At a compaction moment, capture **only the important points NOT yet saved**:
decisions · user constraints/preferences · blockers · current state/milestones.
**Do NOT save** anything derivable from the code or docs (facts, file lists, specs
already written down) — re-derivable content is noise, not memory. No prompting either way.

**RECALL (fast path — one lookup, never a scan):**
- Saves are **keyed at write time**: mem0 `metadata.id` = `MM-<CAT>-<SLUG>`, doc section
  heading = same key, ADR section = same key → recall = ONE targeted lookup, no browsing.
- **Session start / compaction: read THIS file first** — it alone answers terrain
  (folder map), reflex order, timing, and where the rest lives.
- Full recall = **one parallel burst**: `ctx_search` + `mem0.search_memories` +
  `manage_adr(sections)` ≈ **335 ms**. Order: graph (30 ms) → ctx (65 ms) → mem0 (550 ms).
- ADR-008 and mem0 `MM-YT-AUTOSAVE` both point back to THIS §4 — one edit here updates
  all three stores (single source of truth = the recall design itself).

**Every important thing gets written to ALL THREE stores in one pass:**

| # | Store | What to write | How (the exact move) |
|---|---|---|---|
| 1 | **codebase-memory** | anything about code/spec structure | append `ADR-0NN` section via `manage_adr(mode:"update")`; if files changed → `index_repository` re-run |
| 2 | **context-mode** | anything readable/doc-shaped | update the owning file in `system/references/` (or create), then `ctx_index` the same path with its existing **source label** |
| 3 | **mem0** | decision + rationale (short, decision-shaped) | `add_memory` with `metadata:{id:"MM-<CAT>-<SLUG>", type, topic, date}` |

**Stable-ID format (makes every entry easy to READ / UPDATE / DELETE):**
- Key: `MM-<PROJ>-<CAT>-<SLUG>` — PROJ is always **YT** in this project (e.g. `MM-YT-OVERLAY-70S`, `MM-YT-SUB-V22`, `MM-YT-UPLOAD-HOLD`) — used in mem0 `metadata.id`, the doc section heading (`## MM-YT-OVERLAY-70S`), and the ADR title.
- Each entry **cross-references its siblings**: doc says "ADR-001 + mem0 id", mem0 says "file:line", ADR says "KB source". Never orphan an entry.
- One topic = one section = one memory. Never bundle multiple topics into one entry (undiffable).

**RUD cheatsheet (read → update → delete):**
- **READ:** `ctx_search(source label)` + `mem0.search_memories(topic)` + `manage_adr(sections)` — all three in ONE parallel burst (~335 ms).
- **UPDATE:** edit the file section → re-index same path/source → `manage_adr(mode:"update")` with whole doc → mem0: `add_memory` new version with SAME `metadata.id`, then `delete_memory(old_id)` (verify both via `get_event_status`).
- **DELETE:** remove file section → re-index → drop ADR section from doc → `mem0.delete_memory(memory_id)`. Search by `metadata.id` to find the memory id.
- **VERIFY:** mem0 writes `PENDING → get_event_status → SUCCEEDED`; ctx returns section hit; ADR `sections` lists the heading.

## 5. KB SOURCE LABELS (what to query under)

- `Map: codebase category tree` — 108 symbols / 6 categories / tool routing
- `Muscle memory: routing + folder map` — THIS file
- `Spec: youtube system references (v2.2 era)` + `Doc: system dir specs (current)` — all spec values
- `Session checkpoint:*` — what happened this session
- mem0 topics: `overlay` + `ovl-bell-ys` + `ovl-exit`, `subtitle-v2.3` (v2.2 entries deleted 2026-09-26 r2), `upload-hold`, `repo-state`, `libass-gotchas`, `mcp-speed`, `memory-routing`, `architecture`, `mp-revert` (supersedes `mp-landmarker`), `mansion-run`
- codebase-memory: project `D-youtube-system`, ADR-001…010 via `manage_adr`

## 6. RECALL KEYS — session 2026-09-26 (three-store cross-refs)

| Key | One-liner | Stores (doc · ADR · mem0) |
|---|---|---|
| `MM-YT-SUB-V23` | Caption spec **v2.3**: MIXED CASE (no `.upper()`), `\fsp−0.5`, Fontsize 96 kept — user: "38–44px" = cap height, not em. Hook banner + SEO titles stay ALL CAPS. gen_ass.py + all spec docs synced; captions are burned-in → all 15 mansion clips re-encoded | `references/caption-styles.md` v2.3 · ADR-003 r2 · mem0 |
| `MM-YT-MP-REVERT` | **MediaPipe REVERTED to the old BlazeFace `FaceDetector` engine** (user 2026-09-27: "i want all old mediapipe line setting" — landmarker gave worse results; supersedes `MM-YT-MP-LANDMARKER`). `face_track_analyze.py` fully reverted (0 refs to FaceLandmarker / MODEL_LM / FACE_TRACK_ENGINE / RunningMode); bunker pairs were landmarker → DELETED + re-tracked with the old engine; mansion pairs were already old → kept. NEVER reintroduce FaceLandmarker | `face_track_analyze.py` · ADR-010 r2 · mem0 |
| `MM-YT-MANSION-RUN` | Run state COMPLETE: 15/15 ASS v2.3 ✓ · re-encode 15/15 OK (`ENCODE_EXIT=0`, 4-input graph, no bell/YS) · **QC 15/15 PASS** (all 67–72s, LUFS −13.6…−14.6 inside ±0.6 gate; measured-linear fix landed 03=−14.2 04=−14.0 13=−13.9). Sources probed: bunker 1037s/4K · underground 1235s · stranded 2220s · extreme 1407s/4K · HI-mansion 3471s | THIS §6 · mem0 |
| `MM-YT-OVL-BELL-YS` | **Notification Bell + YouTube Subscribe REMOVED permanently** (user 2026-09-26 — froze in place to clip end instead of exiting smoothly; NEVER re-add). Encode graph now EXACTLY 4 inputs `[0]=src [1]=PILL [2]=LCS [3]=CS`; only LCS freeze-held (tpad@4.0). Code + all 5 spec docs synced; grep clean (only intentional "REMOVED" notes remain); mansion 15/15 re-encoded on this graph and QC-passed | `rules.md` · ADR-001 r2 + ADR-002 r2 · mem0 `a7ee722f` ✓ |
| `MM-YT-OVL-EXIT` | **CS overlay: 60→69.4 K-bounce, scale 991 (+20%, user 2026-09-29), x='44.5+495.5*(1-K)' y='534.6+279*(1-K)' re-anchored, hold = `loop=loop=-1:size=1:start=296`** (was 60→END / 826 −15% / x=127 y=584 / setpts+60+gte(t,60)) — asset tail f297–299 is EMPTY: tpad cloned the empty frame → CS died at start+9.87 (the 64.9s vanish); trim/select correct but >6× slower; no-hold dies ~69.9 + repeats empty past 70 (clips run 65.5–74.7s). 6-chain bisect (2026-09-27): loop = gap-free red to 75.9s, 0 absent frames. LCS = full 5s plays 25→30, auto-removed, NO freeze. Code `encode_stage4.py build_fc` + 5 spec docs (21 edits) + `test_build_fc.py` contract synced; `test_build_fc OK` (+20% resync 2026-09-29, probe: 724×200 @ center (539,815)) | `encode_stage4.py` · ADR-002 r3 · mem0 |
