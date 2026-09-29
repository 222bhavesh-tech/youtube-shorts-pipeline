#requires -Version 5
<#
  Archive unused opencode skills to shrink the per-request system prompt.

  SAFETY MODEL
  - Everything in skills\ is git-tracked (repo: ultimate-ai-skills).
  - Archived folders move to skills-archive\ which sits OUTSIDE skills\,
    so opencode stops scanning them and `git restore` can never touch them.
  - Nothing is ever deleted. Rollback script provided.
#>
$ErrorActionPreference = 'Stop'

$root     = "$env:USERPROFILE\.config\opencode\skills"
$archive  = "$env:USERPROFILE\.config\opencode\skills-archive"
$manifest = "$env:USERPROFILE\.config\opencode\skills-archive-MANIFEST.txt"

# ---- KEEP LIST ---------------------------------------------------------
# (a) observed in use, from opencode.log SKILL.md references
$used = @(
  'frontend-patterns','coding-standards','continuous-learning','backend-patterns',
  'tdd-workflow','agent-session-workflow','agent-memory-workflow','nextjs-developer',
  'react-patterns','building-accessible-interfaces','senior-frontend','frontend-developer',
  'security-review','react-expert','frontend-design-systems','continuous-agent-loop',
  'database-migrations','deployment-patterns','context-budget','strategic-compact',
  'postgres-patterns','error-handling','web-design-guidelines','designing-user-experience',
  'autonomous-agent-harness','reviewing-interface-quality','deep-research','cost-tracking',
  'designing-frontend-interfaces','vercel-react-best-practices','clickhouse-io',
  'remotion-animation-rules','remotion-creative-storytelling','api-design'
)
# (b) curated core: media/youtube pipeline + python + shell + workflow + git
$core = @(
  'ffmpeg-skill','viral-video-animated-captions','jenny-tv-srt-tools','youtube-automation',
  'youtube-summarizer','imagen','image-studio','ai-studio-image','stability-ai',
  'comfyui-gateway','keyword-extractor',
  'python-pro','python-patterns','python-testing-patterns',
  'python-performance-optimization','uv-package-manager','python-packaging','fastapi-pro',
  'bash-pro','bash-scripting','os-scripting','powershell-windows',
  'windows-shell-reliability','busybox-on-windows',
  'brainstorming','writing-plans','executing-plans','superpowers','systematic-debugging',
  'verification-before-completion','lint-and-validate','concise-planning','plan-writing',
  'debugger','bug-hunter','error-detective','code-simplifier','simplify-code','find-bugs',
  'code-review','code-review-checklist','security-audit','moyu',
  'commit','git-pushing','github','create-branch','issues','address-github-comments',
  'create-pr','iterate-pr','finishing-a-development-branch',
  'context-guardian','diary','structured-project-execution','planning-with-files',
  'agents-md','readme','documentation','opencode'
)
$keep = $used + $core | Sort-Object -Unique

# ---- discovery ---------------------------------------------------------
if (-not (Test-Path $root))    { Write-Host "ABORT: $root missing"; exit 1 }
if (-not (Test-Path "$root\.git")) { Write-Host "ABORT: skills\ is not a git repo - no safety net"; exit 1 }

$top = Get-ChildItem $root -Directory -Force | Where-Object { $_.Name -notlike '.*' }
$keepSet = New-Object 'System.Collections.Generic.HashSet[string]'

foreach ($d in $top) {
  $sk = Get-ChildItem $d.FullName -Recurse -Filter 'SKILL.md' -File -ErrorAction SilentlyContinue
  if ($sk.Count -gt 1) { [void]$keepSet.Add($d.Name); continue }   # bundles sub-skills: keep
  if ($sk.Count -eq 1 -and $keep -contains $d.Name) { [void]$keepSet.Add($d.Name) }
}

$toArchive = $top | Where-Object { -not $keepSet.Contains($_.Name) }

# ---- verify every keeper exists, warn on misses ------------------------
$miss = $keep | Where-Object { -not (Test-Path (Join-Path $root $_)) }
Write-Host ""
Write-Host "  total skill folders : $($top.Count)"
Write-Host "  KEEP                : $($keepSet.Count)"
Write-Host "  ARCHIVE             : $($toArchive.Count)"
if ($miss) { Write-Host "  (not installed, skipped: $($miss -join ', '))" }
Write-Host ""

if ($keepSet.Count -lt 40) { Write-Host "ABORT: keeper list too small ($($keepSet.Count)) - something is wrong"; exit 1 }
if ($toArchive.Count -lt 100) { Write-Host "ABORT: nothing meaningful to archive"; exit 1 }

if ($args -contains '-WhatIf') { Write-Host "WHATIF: no changes made."; exit 0 }

# ---- execute -----------------------------------------------------------
New-Item -ItemType Directory -Path $archive -Force | Out-Null
"# opencode skills archive  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Set-Content $manifest
"# rollback: powershell -File `"D:\youtube system\.opencode\rollback-skills.ps1`"" | Add-Content $manifest

$moved = 0
foreach ($d in $toArchive) {
  $dest = Join-Path $archive $d.Name
  if (Test-Path $dest) { $dest = Join-Path $archive ("{0}__{1}" -f $d.Name, (Get-Random -Maximum 9999)) }
  Move-Item -LiteralPath $d.FullName -Destination $dest -Force
  "MOVED: $($d.Name)" | Add-Content $manifest
  $moved++
}

Write-Host "moved $moved folders to $archive"
Write-Host "manifest: $manifest"
Write-Host ""
Write-Host "=== RESULT ==="
"  live skills  : $((Get-ChildItem $root -Directory -Force | Where-Object { $_.Name -notlike '.*' }).Count)"
"  archived     : $((Get-ChildItem $archive -Directory).Count)"
