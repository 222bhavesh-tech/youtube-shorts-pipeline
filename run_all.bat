@echo off
REM run_all.bat [upload] [profile.json ...]
REM Batch driver: kills any overlay-loop remnant (Phase-0 guard), then runs
REM the full pipeline for each profile (default: bunker + mansion).
REM   run_all.bat                        -> prep..SEO, no upload
REM   run_all.bat upload                 -> + stage 7 (EXPLICIT HUMAN PASS ONLY)
REM   run_all.bat system\profiles\bn0.json
setlocal enabledelayedexpansion
cd /d "D:\youtube system"

echo [guard] killing autonomous-loop / apply_overlay remnants...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'autonomous-loop|apply_overlay' -and $_.Name -notmatch 'powershell|cmd' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"

set FLAGS=
set PROFILES=
:parse
if "%~1"=="" goto run
if /i "%~1"=="upload" (
    set FLAGS=--upload
) else (
    set PROFILES=!PROFILES! "%~f1"
)
shift
goto parse

:run
if "%PROFILES%"=="" set PROFILES= "D:\youtube system\system\profiles\bunker.json" "D:\youtube system\system\profiles\mansion.json" "D:\youtube system\system\profiles\bn0.json" "D:\youtube system\system\profiles\stranded.json" "D:\youtube system\system\profiles\mansion_hi.json" "D:\youtube system\system\profiles\g3.json"

for %%P in (%PROFILES%) do (
    echo.
    echo ========== %%~nxP ==========
    python -X utf8 "D:\youtube system\system\run_pipeline.py" "%%~P" %FLAGS%
    if errorlevel 1 (
        echo RUN_ALL FAILED on %%~nxP
        exit /b 1
    )
)

echo.
echo RUN_ALL DONE
exit /b 0
