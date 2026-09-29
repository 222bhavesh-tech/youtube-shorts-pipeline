# Codebase Map — categorized node graph (fast lookup)

> Generated 2026-09-26 from codebase-memory-mcp (`D-youtube-system`, 1913 nodes / 3326 edges).
> Purpose: answer "where is X / who calls Y" WITHOUT reading files. Query the graph first,
> fall back to grep only for literal text.

## Graph facts

| Metric | Value |
|---|---|
| Nodes / edges | 1913 / 3326 |
| Node labels | Variable 1301, Section 194, File 134, Module 134, Function 110, Folder 12, Package 10, Class 5, EnvVar 5, Method 5 |
| Edge types | DEFINES 2025, CALLS 327, USAGE 326, WRITES 226, CONTAINS_FILE 134, CONFIGURES 121, SEMANTICALLY_RELATED 105, IMPORTS 15 |
| Languages | Python 24 files, Bash 8 files |
| Packages | Pillow, google-api-python-client, google-auth-httplib2, google-auth-oauthlib, isodate, mcp, nltk, python-dotenv, requests, youtube-transcript-api |
| Entry points | `encode_stage4.main`, `gen_ass.main`, `prep_stage4.main`, `qc_stage5.main`, `ab_rotate.main`, `authorize.main` |

## Category tree (108 project symbols)

### 1. PIPELINE — production stages (steps 1→7)
- `system.slice_transcript` — ts_to_sec
- `system.select_moments` — pick_start, snap_back_cut, hook_ok  ← 70s window logic
- `system.face_track_analyze` — build, segs, seg, fmt, expr_nesting
- `system.prep_stage4` — main, run, face, ass_and_hook
- `system.encode_stage4` — main, encode, build_fc, loudnorm_chain  ← stacked overlay graph + `-t DUR`
- `system.qc_stage5` — main, qc, run, probe, last_yavg, integrated_lufs  ← 65–120s gate
- `system.final_lock` — Check, Warn  ← asserts "70"
- `system.test_build_fc` (test module)

### 2. CAPTIONS — subtitle spec v2.3
- `system.gen_ass` — main, ts_to_sec, sec_to_ass, chunk_words, wrap_lines, build_line_text  ← TRACKING=-4 / ACTIVE_RISE
- `system.qc_boundaries` — is_sent_start
- `system.vtt2srt` — fmt

### 3. OVERLAY / FUNCLIP — animated overlay builders + suites
- `funclip-overlay._mkoverlays` — font, pill
- `funclip-overlay._system` — staged_name
- Tests (65/65 GREEN): `_test` (ok, bad, mk, bright, chk), `_test2` (ok, bad), `_test3` (ok, bad, mk360, mk1080, SYSENV)

### 4. MCP — YouTube upload / channel ops
- `youtube-mcp-server.auth` — youtube_data **(hotspot, fan-in 11)**, youtube_analytics, load_credentials, client_config, token_path, state_dir
- `youtube-mcp-server.server` — youtube_upload, youtube_update_metadata, youtube_set_thumbnail, youtube_whoami, youtube_list_uploads, youtube_playlist_create/add, youtube_analytics, youtube_seo_audit, youtube_competitor_tags, ab rotate (youtube_ab_start/rotate/report + _load_ledger/_save_ledger/_set_thumb/_ab_ledger_path/_my_channel_id/_now_iso)
- `youtube-mcp-server.ab_rotate` — main
- `youtube-mcp-server.authorize` — main

### 5. MCP — YouTube SEO / research
- `youtube-mcp-seo.main` (24 fns) — resolve_channel_id, get_channel_{overview,topics,videos}, get_top_videos, get_trending_videos, get_video_{details,comments,transcript,seo_score}, get_upload_schedule, get_engagement_stats, get_tag_analysis, get_comment_keywords, compare_{channels,videos}, analyze_thumbnail, get_uploads_playlist_id, helpers (`_get` hotspot fan-in 11, `_safe_int`, `_safe_float`, `_thumbnail_url`, `_fetch_videos_for_channel`, `_parse_duration`)
- `youtube-mcp-seo.server` — run, list_tools, call_tool, _dispatch

### 6. BATCH DRIVERS — PowerShell concurrency (GPU cap 2)
- `pairs_drive.Run-Two`, `pairs_drive_g3`, `pairs_drive_v1`, `pairs_drive_v2`, `parse_v1.W`

## Layers (from graph)

| Layer | Members | Why |
|---|---|---|
| entry | encode_stage4, gen_ass, youtube-mcp-server | entry points, outbound-only |
| internal | prep_stage4, qc_stage5 | no resolved cross-calls (CLI-invoked) |
| core | builtins dict/list/len/str | high fan-in |
| leaf | face_track_analyze, print | inbound-only |

## Change impact since `d2b9e2a` (uncommitted work)

`detect_changes(since=d2b9e2a, inbound)` → **10 impacted modules, all hop 1**:
`final_lock.ps1`, `test_build_fc.py`, `qc_stage5.py`, `qc_boundaries.py`, `select_moments.py`,
`slice_transcript.py`, `youtube-mcp-server/server.py`, `encode_stage4.py`, `prep_stage4.py`, `gen_ass.py`
(124 changed files total — rest are `output/final clips/**/metadata/*.txt` artifacts.)

## Fast-lookup routing (which tool, first try)

| Question | Tool (in order) |
|---|---|
| Who calls X / blast radius of an edit | `trace_path` → `detect_changes` |
| Find symbol by pattern/name | `search_graph(name_pattern=…)` or `query_graph` Cypher |
| Architecture, layers, clusters, hotspots | `get_architecture(aspects=[…])` |
| Literal text, non-code, .md/.ps1 content | grep / `ctx_search` (graph misses PS1 ranges) |
| Large data analysis, multi-command runs | `ctx_execute` / `ctx_batch_execute` |
| Why a decision exists, what was decided | `mem0.search_memories` FIRST |
| Current spec values (70s / v2.3 / upload) | `ctx_search` on `Spec:*` + `Decision:*` sources |

## Known index gaps

- `.ps1` files (`qc_g3/qc_new/qc_v1/report_final/verify_v2`) are `parse_partial` — some constructs
  inside listed line ranges may be missing → prefer grep for PowerShell internals.
- `.env`, `client_secret.json` gitignored (by design). `system/assets` skipped.
- No ADR section existed before 2026-09-26 (see `manage_adr` → D-youtube-system).
