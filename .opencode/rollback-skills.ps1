#requires -Version 5
# Rollback: move archived skills back into the live skills folder.
$ErrorActionPreference = 'Stop'
$root    = "$env:USERPROFILE\.config\opencode\skills"
$archive = "$env:USERPROFILE\.config\opencode\skills-archive"
$manifest= "$env:USERPROFILE\.config\opencode\skills-archive-MANIFEST.txt"

if (-not (Test-Path $manifest)) { Write-Host "No manifest found at $manifest"; exit 1 }

$lines = Get-Content $manifest | Where-Object { $_ -like 'MOVED:*' }
Write-Host "Restoring $($lines.Count) skills..."
$n = 0
foreach ($l in $lines) {
  $path = ($l -replace '^MOVED:\s*\S+\s*->\s*', '')
  if (-not (Test-Path $path)) { continue }
  $name = Split-Path $path -Leaf
  $target = Join-Path $root ($name -replace '__\d+$','')
  if (Test-Path $target) { continue }
  Move-Item -LiteralPath $path -Destination $target -Force
  $n++
}
Write-Host "Restored $n skills."
