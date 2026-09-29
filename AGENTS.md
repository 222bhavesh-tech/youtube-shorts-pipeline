# Rules
Read and follow D:\youtube system\system\rules.md

## context-mode - MANDATORY routing rules

context-mode tools available. Rules protect context window from flooding. One unrouted command dumps 56 KB into context.

### Think in Code - MANDATORY

Analyze/count/filter/compare/search/parse/transform data: **write code** via `context-mode_ctx_execute(language, code)`, `console.log()` only the answer. Do NOT read raw data into context. PROGRAM the analysis, not COMPUTE it. Pure JavaScript - Node.js built-ins only (`fs`, `path`, `child_process`). `try/catch`, handle `null`/`undefined`. One script replaces ten tool calls.

### BLOCKED - do NOT attempt

- `curl` / `wget` - Shell intercepted and blocked. Do NOT retry. Use `context-mode_ctx_fetch_and_index(url, source)` or `context-mode_ctx_execute(language: "javascript", code: "const r = await fetch(...)")`
- Inline HTTP - `fetch('http`, `requests.get(`, `requests.post(`, `http.get(`, `http.request(` intercepted. Do NOT retry. Use `context-mode_ctx_execute(language, code)` - only stdout enters context.
- Direct web fetching - Use `context-mode_ctx_fetch_and_index(url, source)` then `context-mode_ctx_search(queries)`

### REDIRECTED - use sandbox

- Shell (>20 lines output): Shell ONLY for `git`, `mkdir`, `rm`, `mv`, `cd`, `ls`, `npm install`, `pip install`. Otherwise `context-mode_ctx_batch_execute(commands, queries)` or `context-mode_ctx_execute(language, code)`. Use `language: "shell"` only when code matches the host shell.
- File reading (for analysis): Reading to **edit** = reading correct. Reading to **analyze/explore/summarize** = `context-mode_ctx_execute_file(path, language, code)`.
- grep / search (large results): Use `context-mode_ctx_execute(language: "javascript", code: "...")` in sandbox for portable filtering/counting.

### Tool selection

0. **MEMORY**: `context-mode_ctx_search(sort: "timeline")` - after resume, check prior context before asking user.
1. **GATHER**: `context-mode_ctx_batch_execute(commands, queries)` - runs all commands, auto-indexes, returns search. ONE call replaces 30+. Each command: `{label: "header", command: "..."}`.
2. **FOLLOW-UP**: `context-mode_ctx_search(queries: ["q1", "q2", ...])` - all questions as array, ONE call (default relevance mode).
3. **PROCESSING**: `context-mode_ctx_execute(language, code)` | `context-mode_ctx_execute_file(path, language, code)` - sandbox, only stdout enters context.
4. **WEB**: `context-mode_ctx_fetch_and_index(url, source)` then `context-mode_ctx_search(queries)` - raw HTML never enters context.
5. **INDEX**: `context-mode_ctx_index(content, source)` - store in FTS5 for later search.

### Parallel I/O batches

For multi-URL fetches or multi-API calls, **always** include `concurrency: N` (1-8):

- `context-mode_ctx_batch_execute(commands: [3+ network commands], concurrency: 5)` - gh, curl, dig, docker inspect, multi-region cloud queries
- `context-mode_ctx_fetch_and_index(requests: [{url, source}, ...], concurrency: 5)` - multi-URL batch fetch

**Use concurrency 4-8** for I/O-bound work. **Keep concurrency 1** for CPU-bound (npm test, build, lint) or commands sharing state (ports, lock files, same-repo writes). GitHub API rate-limit: cap at 4 for `gh` calls.

### Output

Write artifacts to FILES - never inline. Return: file path + 1-line description. Descriptive source labels for `search(source: "label")`.

### Session Continuity

Skills, roles, and decisions persist for the entire session. Do not abandon them as the conversation grows.

### Memory

Session history is persistent and searchable. On resume, search BEFORE asking the user:

| Need | Command |
|------|---------|
| What did we decide? | `context-mode_ctx_search(queries: ["decision"], source: "decision", sort: "timeline")` |
| What constraints exist? | `context-mode_ctx_search(queries: ["constraint"], source: "constraint")` |

DO NOT ask "what were we working on?" - SEARCH FIRST. If search returns 0 results, proceed as a fresh session.

### ctx commands

| Command | Action |
|---------|--------|
| `ctx stats` | Call `stats` MCP tool, display full output verbatim |
| `ctx doctor` | Call `doctor` MCP tool, run returned shell command, display as checklist |
| `ctx upgrade` | Call `upgrade` MCP tool, run returned shell command, display as checklist |
| `ctx purge` | Call `purge` MCP tool with confirm: true. Warns before wiping knowledge base. |

After /clear or /compact: knowledge base and session stats preserved. Use `ctx purge` to start fresh.

## Memory systems - routing (context-mode | Mem0 | codebase-memory-mcp)

Three memory stores, one rule: **ephemeral analysis → context-mode, durable decisions → Mem0, structural facts about code → codebase-memory-mcp.** Overlap is fine; re-deriving is more expensive than storing.

| Question | System | Tool |
|----------|--------|------|
| What happened / did we decide THIS session? | context-mode | `ctx_search` |
| What did we decide ACROSS sessions? | Mem0 | `mem0.search_memories` |
| Who calls X / find all *Handler* / architecture / git-diff impact | codebase-memory-mcp | `trace_path`, `search_graph`, `get_architecture`, `detect_changes`, `get_code_snippet`, `query_graph` |
| Analyze/count/filter big data or files | context-mode | `ctx_execute` / `ctx_execute_file` (only stdout enters context) |
| Multi-command runs (test+lint+diff) | context-mode | `ctx_batch_execute` |

### Mem0 - MANUAL ONLY (OpenCode V2: no plugin hooks)

There are NO auto-save/auto-inject hooks on V2 — Mem0 only acts when explicitly called. Proactive rules:

- User says "Remember: X" → `mem0.add_memory` immediately.
- User asks "what do you know about X" → `mem0.search_memories` FIRST, answer from results.
- End of a substantial task/session where decisions, constraints, or user prefs were established → offer to save them to Mem0 (or do it if the user already asked to keep notes). Keep entries short, decision-shaped: context → decision → rationale.
- "Forget about X" → confirm memory_id, then `mem0.delete_memory`.

### codebase-memory-mcp

If repo not indexed yet (`list_projects` shows no entry): run `index_repository` once before graph queries. Use graph FIRST for structural discovery (symbols, callers/callees, multi-hop); fall back to grep/`search_code` for literal or non-code text. Check `check_index_coverage` before making strong negative claims ("no callers exist").
