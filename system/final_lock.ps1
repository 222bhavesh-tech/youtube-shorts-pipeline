# ═══════════════════════════════════════════════════════════════════
# FINAL REFINE + POLISH + REPAIR + LOCK
# Run once. After this, system is stable.
# ═══════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Continue"
$py = "C:\Users\bhavesh jeengar\AppData\Local\Programs\Python\Python312\python.exe"
$yt = "D:\youtube system"
$pass = 0
$fail = 0
$warn = 0

function Check($name, $condition, $fix) {
    if ($condition) {
        Write-Host "  ✅ $name" -ForegroundColor Green
        $script:pass++
    } else {
        Write-Host "  ❌ $name" -ForegroundColor Red
        if ($fix) { Write-Host "     Fix: $fix" -ForegroundColor Yellow }
        $script:fail++
    }
}

function Warn($name, $condition, $note) {
    if ($condition) {
        Write-Host "  ⚠️  $name — $note" -ForegroundColor Yellow
        $script:warn++
    }
}

Write-Host "`n═════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  FINAL AUDIT + REPAIR + LOCK" -ForegroundColor Cyan
Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "═════════════════════════════════════════════════════════" -ForegroundColor Cyan

# ───────────────────────────────────────────────────────────────────
Write-Host "`n── 1. FOLDERS ──" -ForegroundColor Yellow

$folders = @(
    "$yt\output\4k video",
    "$yt\output\4k video\en",
    "$yt\output\4k video\hi",
    "$yt\output\transcript",
    "$yt\output\transcript\en",
    "$yt\output\transcript\hi",
    "$yt\output\face_track",
    "$yt\output\face_track\en",
    "$yt\output\face_track\hi",
    "$yt\output\final clips",
    "$yt\output",
    "$yt\system\references",
    "$yt\system\assets",
    "$yt\system\youtube-mcp-server",
    "$yt\system\youtube-mcp-seo"
)
foreach ($f in $folders) {
    if (Test-Path $f) { Check "$(Split-Path $f -Leaf)" $true $null }
    else {
        New-Item -ItemType Directory -Force -Path $f | Out-Null
        Write-Host "  🆕 Created: $(Split-Path $f -Leaf)" -ForegroundColor Green
        $script:pass++
    }
}

# ───────────────────────────────────────────────────────────────────
Write-Host "`n── 2. CORE FILES ──" -ForegroundColor Yellow

$files = @{
    "$yt\system\rules.md" = 200
    "$yt\AGENTS.md" = 30
    "$yt\GEMINI.md" = 30
    "$yt\system\SKILL.md" = 500
    "$yt\system\references\tool-routing.md" = 100
    "$yt\system\references\caption-styles.md" = 100
    "$yt\system\references\encoding-settings.md" = 50
    "$yt\system\references\error-handling.md" = 50
    "$yt\system\references\mcp-tools.md" = 50
}
foreach ($pair in $files.GetEnumerator()) {
    $path = $pair.Key
    $minSize = $pair.Value
    if (Test-Path $path) {
        $size = (Get-Item $path).Length
        if ($size -ge $minSize) {
            Check "$(Split-Path $path -Leaf) ($size B)" $true $null
        } else {
            Check "$(Split-Path $path -Leaf) — CORRUPT ($size B, need >$minSize)" $false "Recreate this file"
        }
    } else {
        Check "$(Split-Path $path -Leaf) — MISSING" $false "Create this file"
    }
}

# ───────────────────────────────────────────────────────────────────
Write-Host "`n── 3. BINDING CHAIN ──" -ForegroundColor Yellow

$agentsContent = if (Test-Path "$yt\AGENTS.md") { Get-Content "$yt\AGENTS.md" -Raw } else { "" }
$geminiContent = if (Test-Path "$yt\GEMINI.md") { Get-Content "$yt\GEMINI.md" -Raw } else { "" }
$rulesContent = if (Test-Path "$yt\system\rules.md") { Get-Content "$yt\system\rules.md" -Raw } else { "" }

Check "AGENTS.md → rules.md" ($agentsContent -match "rules\.md") "AGENTS.md must contain 'Read and follow D:\youtube system\system\rules.md'"
Check "GEMINI.md → rules.md" ($geminiContent -match "rules\.md") "GEMINI.md must contain 'Read and follow D:\youtube system\system\rules.md'"
Check "rules.md → SKILL.md" ($rulesContent -match "SKILL\.md") "rules.md must reference SKILL.md"
Check "rules.md → tool-routing.md" ($rulesContent -match "tool-routing") "rules.md must reference tool-routing.md"
Check "rules.md has 'NEVER upload'" ($rulesContent -match "NEVER upload") "Add upload gate rule"
Check "rules.md has '70 seconds'" ($rulesContent -match "70") "Add duration rule"

# ───────────────────────────────────────────────────────────────────
Write-Host "`n── 4. PYTHON + PACKAGES ──" -ForegroundColor Yellow

Check "Python 3.12" (& $py --version 2>&1 -match "3\.12") "Install Python 3.12"

$pkgs = @{
    "yt-dlp" = "yt_dlp"
    "mediapipe" = "mediapipe"
    "cv2 (opencv)" = "cv2"
    "PIL (pillow)" = "PIL"
    "gradio_client" = "gradio_client"
}
foreach ($pair in $pkgs.GetEnumerator()) {
    $result = & $py -c "import $($pair.Value)" 2>&1
    Check "$($pair.Key)" ($LASTEXITCODE -eq 0) "pip install $($pair.Key)"
}

# ───────────────────────────────────────────────────────────────────
Write-Host "`n── 5. FFMPEG ──" -ForegroundColor Yellow

$ffmpeg = "D:\FunClip\tools\ffmpeg\bin\ffmpeg.exe"
$ffprobe = "D:\FunClip\tools\ffmpeg\bin\ffprobe.exe"

Check "ffmpeg.exe" (Test-Path $ffmpeg) "Install FFmpeg"
Check "ffprobe.exe" (Test-Path $ffprobe) "Install FFmpeg"

if (Test-Path $ffmpeg) {
    $ver = & $ffmpeg -version 2>&1 | Select-Object -First 1
    Check "ffmpeg version" ($ver -match "ffmpeg version") $null
    Write-Host "     $ver" -ForegroundColor DarkGray
}

# Check critical filters
$filters = & $ffmpeg -filters 2>&1
foreach ($f in @("gblur", "overlay", "drawtext", "ass", "loudnorm", "silenceremove", "fade", "afade", "eq", "scale", "crop")) {
    Check "filter: $f" ($filters -match $f) "FFmpeg build missing $f"
}

# ───────────────────────────────────────────────────────────────────
Write-Host "`n── 6. MCP CONFIG (OpenCode) ──" -ForegroundColor Yellow

$ocPath = "$env:USERPROFILE\.config\opencode\opencode.json"
if (Test-Path $ocPath) {
    $oc = Get-Content $ocPath -Raw
    Check "opencode.json exists" $true $null
    Check "youtube MCP in config" ($oc -match "youtube-mcp-server") "Add youtube entry"
    Check "youtube-seo MCP in config" ($oc -match "youtube-mcp-seo") "Add youtube-seo entry"
} else {
    Check "opencode.json" $false "Create at $ocPath"
}

# ───────────────────────────────────────────────────────────────────
Write-Host "`n── 7. MCP CONFIG (Antigravity) ──" -ForegroundColor Yellow

$agPath = "$env:USERPROFILE\.gemini\config\mcp_config.json"
if (Test-Path $agPath) {
    $ag = Get-Content $agPath -Raw
    Check "mcp_config.json exists" $true $null
    Check "youtube MCP" ($ag -match "youtube-mcp-server") "Add youtube entry"
    Check "youtube-seo MCP" ($ag -match "youtube-mcp-seo") "Add youtube-seo entry"
} else {
    Check "mcp_config.json" $false "Create at $agPath"
}

# ───────────────────────────────────────────────────────────────────
Write-Host "`n── 8. YOUTUBE MCP SERVER ──" -ForegroundColor Yellow

Check "server.py" (Test-Path "$yt\system\youtube-mcp-server\server.py") "git clone jayadevrana/youtube-mcp-server"
Check "client_secret.json" (Test-Path "$yt\system\youtube-mcp-server\client_secret.json") "Download from Google Cloud"

# ───────────────────────────────────────────────────────────────────
Write-Host "`n── 9. YOUTUBE-SEO MCP SERVER ──" -ForegroundColor Yellow

Check "server.py" (Test-Path "$yt\system\youtube-mcp-seo\server.py") "git clone Yashkashte5/Youtube-MCP"
$envFile = "$yt\system\youtube-mcp-seo\.env"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    Check ".env has API key" ($envContent -match "YOUTUBE_API_KEY=AIza") "Set YOUTUBE_API_KEY=AIza..."
} else {
    Check ".env" $false "Create .env with YOUTUBE_API_KEY"
}

# ───────────────────────────────────────────────────────────────────
Write-Host "`n── 10. FUNCLIP BACKUP ──" -ForegroundColor Yellow

Check "FunClip folder" (Test-Path "D:\FunClip\funclip") "Install FunClip"
Check "FunClip venv" (Test-Path "D:\FunClip.venv\Scripts\activate.bat") "Create venv"
Check "run_funclip_headless.bat" (Test-Path "$yt\system\run_funclip_headless.bat") "Create bat file"

# ───────────────────────────────────────────────────────────────────
Write-Host "`n── 11. ASSETS ──" -ForegroundColor Yellow

Check "hook_pill.png" (Test-Path "$yt\system\assets\hook_pill.png") "Generate with PIL script"

# ───────────────────────────────────────────────────────────────────
Write-Host "`n── 12. CLEANUP ──" -ForegroundColor Yellow

# Stray files in root
$allowed = @(".md", ".bat", ".json", ".gitignore", ".ps1")
$strays = Get-ChildItem $yt -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -notin $allowed }
if ($strays) {
    foreach ($s in $strays) {
        Write-Host "  🗑️  Removing: $($s.Name)" -ForegroundColor DarkYellow
        Remove-Item $s.FullName -Force
    }
} else {
    Write-Host "  ✅ No stray files" -ForegroundColor Green
    $script:pass++
}

# Empty folders
$empty = Get-ChildItem $yt -Directory -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notin @("$yt\output\4k video","$yt\output\4k video\en","$yt\output\4k video\hi","$yt\output\transcript","$yt\output\transcript\en","$yt\output\transcript\hi","$yt\output\face_track","$yt\output\face_track\en","$yt\output\face_track\hi","$yt\output","$yt\system\references","$yt\system\assets") -and $_.FullName -notlike "$yt\output\final clips\*" -and -not (Get-ChildItem $_.FullName -Force -ErrorAction SilentlyContinue) }
foreach ($e in $empty) {
    Write-Host "  🗑️  Removing empty: $($e.FullName)" -ForegroundColor DarkYellow
    Remove-Item $e.FullName -Force
}

# ───────────────────────────────────────────────────────────────────
Write-Host "`n── 13. LIVE TEST ──" -ForegroundColor Yellow

# Test yt-dlp
$ytdlp = & $py -m yt_dlp --version 2>&1
Check "yt-dlp runs" ($ytdlp -match "\d+\.\d+") "pip install yt-dlp"

# Test MediaPipe — legacy mp.solutions was removed from modern mediapipe (1.0.1, 0.10.35);
# test the Tasks API + model asset that face_track_analyze.py (Mode A) actually uses
$mp = & $py -c "from mediapipe.tasks import python as mpp; from mediapipe.tasks.python import vision; d=vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(base_options=mpp.BaseOptions(model_asset_path=r'D:\youtube system\system\assets\models\face_detector.tflite'))); print('ok')" 2>&1
Check "MediaPipe face detection" ($mp -match "ok") "pip install mediapipe"

# Test PIL
$pil = & $py -c "from PIL import Image, ImageDraw; img=Image.new('RGBA',(10,10)); d=ImageDraw.Draw(img); d.rounded_rectangle([(0,0),(9,9)],radius=3,fill=(255,255,255,200)); print('ok')" 2>&1
Check "PIL rounded_rectangle" ($pil -match "ok") "pip install Pillow"

# Test FFmpeg can actually encode (1 second silent test)
$testOut = "$yt\_test_encode.mp4"
& $ffmpeg -y -f lavfi -i "sine=frequency=440:duration=1" -f lavfi -i "color=c=black:s=1080x1920:d=1" -c:v libx264 -crf 18 -preset ultrafast -c:a aac -shortest $testOut 2>$null
Check "FFmpeg encode test" (Test-Path $testOut) "FFmpeg broken"
if (Test-Path $testOut) { Remove-Item $testOut -Force }

# Test FFmpeg filter_complex (3-zone)
$testOut2 = "$yt\_test_3zone.mp4"
& $ffmpeg -y -f lavfi -i "color=c=blue:s=1920x1080:d=1" -filter_complex "[0:v]split[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.25[bg2];[fg]scale=1080:864:force_original_aspect_ratio=increase,crop=1080:864[fg2];[bg2][fg2]overlay=0:384" -c:v libx264 -crf 18 -preset ultrafast -an $testOut2 2>$null
Check "FFmpeg 3-zone filter" (Test-Path $testOut2) "Filter complex broken"
if (Test-Path $testOut2) { Remove-Item $testOut2 -Force }

# Test FFmpeg drawtext (hook pill)
$testOut3 = "$yt\_test_pill.mp4"
& $ffmpeg -y -f lavfi -i "color=c=black:s=1080x1920:d=1" -vf "drawtext=text='TEST HOOK':fontfile='C\:/Windows/Fonts/arialbd.ttf':fontsize=40:fontcolor=black:box=1:boxcolor=white@0.92:boxborderw=15:x=(w-text_w)/2:y=84" -c:v libx264 -crf 18 -preset ultrafast -an $testOut3 2>$null
Check "FFmpeg drawtext (pill)" (Test-Path $testOut3) "drawtext broken"
if (Test-Path $testOut3) { Remove-Item $testOut3 -Force }

# Test FFmpeg loudnorm
$testOut4 = "$yt\_test_loud.mp4"
& $ffmpeg -y -f lavfi -i "sine=frequency=440:duration=2" -af "loudnorm=I=-14:TP=-1:LRA=11" -c:a aac $testOut4 2>$null
Check "FFmpeg loudnorm" (Test-Path $testOut4) "loudnorm broken"
if (Test-Path $testOut4) { Remove-Item $testOut4 -Force }

# ───────────────────────────────────────────────────────────────────
Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  FINAL REPORT" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ✅ Passed:  $pass" -ForegroundColor Green
Write-Host "  ❌ Failed:  $fail" -ForegroundColor Red
Write-Host "  ⚠️  Warnings: $warn" -ForegroundColor Yellow
Write-Host ""

if ($fail -eq 0) {
    Write-Host "  ╔══════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "  ║  SYSTEM LOCKED. FULLY OPERATIONAL.           ║" -ForegroundColor Green
    Write-Host "  ║  Type 'youtube system' to start.             ║" -ForegroundColor Green
    Write-Host "  ╚══════════════════════════════════════════════╝" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  $fail issue(s) found. Fix above, re-run this script." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Final structure:" -ForegroundColor Cyan
Get-ChildItem $yt -Depth 1 | Where-Object { $_.PSIsContainer -or $_.Extension -in @(".md",".bat") } | ForEach-Object {
    $indent = if ($_.PSIsContainer) { "📁" } else { "📄" }
    Write-Host "  $indent $($_.Name)" -ForegroundColor DarkGray
}
Write-Host ""
