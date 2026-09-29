param([string]$NN)
$ErrorActionPreference = "Continue"
$env:CUDA_VISIBLE_DEVICES = $null   # opencode server env may still carry -1 (GPU hidden)
$ffp = "D:\FunClip\tools\ffmpeg\bin\ffprobe.exe"
$ff  = "C:\Users\bhavesh jeengar\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"
$py  = "C:\Users\bhavesh jeengar\AppData\Local\Programs\Python\Python312\python.exe"
Set-Location "D:\youtube system\output\temp"   # relative metadata=print:file= must land in temp, NOT root

$wins = @{
 "01"=@{s=0.267;     e=86.353;   slug="death_rules"}
 "02"=@{s=87.033;    e=167.734;  slug="antarctic_whiteout"}
 "03"=@{s=168.100;   e=250.517;  slug="bridge_for_wife"}
 "04"=@{s=252.834;   e=329.396;  slug="cliff_60lb_climb"}
 "05"=@{s=339.868;   e=417.384;  slug="threw_away_food"}
 "06"=@{s=417.834;   e=493.827;  slug="anaconda_river"}
 "07"=@{s=493.868;   e=574.374;  slug="dead_mans_raft"}
 "08"=@{s=646.200;   e=725.058;  slug="zip_tie_raft"}
 "09"=@{s=726.767;   e=816.649;  slug="wrong_way_sea"}
 "10"=@{s=816.834;   e=892.825;  slug="not_losing_jimmy"}
 "11"=@{s=893.200;   e=979.445;  slug="five_more_hills"}
 "12"=@{s=980.734;   e=1060.560; slug="dropped_backpack"}
 "13"=@{s=1062.000;  e=1142.742; slug="spider_bite"}
 "14"=@{s=1296.334;  e=1399.131; slug="helicopter_win"}
}
if (-not $wins.ContainsKey($NN)) { throw "unknown clip $NN" }
$w = $wins[$NN]
$DUR = [math]::Round($w.e - $w.s, 3)

$proj   = "D:\youtube system\output\final clips\extreme\en\I Survived Extreme Places"
$tmpout = "$proj\clips\${NN}_$($w.slug).mp4"

if (-not (Test-Path -LiteralPath $tmpout)) { throw "missing $tmpout" }

# ---- 1. stream / duration / size gate ----
$probe = & $ffp -v error -show_entries format=duration,size -show_entries stream=index,codec_type,codec_name,width,height,pix_fmt,avg_frame_rate,sample_rate,channels -of json $tmpout | ConvertFrom-Json
$vid = $probe.streams | Where-Object { $_.codec_type -eq "video" }
$aud = $probe.streams | Where-Object { $_.codec_type -eq "audio" }
$nstreams = $probe.streams.Count
$cdur = [double]$probe.format.duration
$size = [long]$probe.format.size

$fail = @()
if ($nstreams -ne 2) { $fail += "streams=$nstreams" }
if ($vid.codec_name -ne "h264") { $fail += "vcodec=$($vid.codec_name)" }
if ("$($vid.width)x$($vid.height)" -ne "1080x1920") { $fail += "res=$($vid.width)x$($vid.height)" }
if ($vid.pix_fmt -ne "yuv420p") { $fail += "pix=$($vid.pix_fmt)" }
if ($vid.avg_frame_rate -ne "30000/1001") { $fail += "fps=$($vid.avg_frame_rate)" }
if ($aud.codec_name -ne "aac") { $fail += "acodec=$($aud.codec_name)" }
if ($aud.sample_rate -ne "48000") { $fail += "sr=$($aud.sample_rate)" }
if ($cdur -lt 75 -or $cdur -gt 120) { $fail += "dur=$cdur" }
if ($size -ge 2GB) { $fail += "size=$size" }
"QC streams: dur=$([math]::Round($cdur,2)) size=$size v=$($vid.avg_frame_rate) " + $(if ($fail) { "FAIL: " + ($fail -join '; ') } else { "OK" })

# ---- 2. TRUE last-frame YAVG: decode final 0.3s (-sseof), take LAST frame (fade complete -> Y~16) ----
$yavgFile = "D:\youtube system\output\temp\yavg$NN.txt"
if (Test-Path -LiteralPath $yavgFile) { Remove-Item -LiteralPath $yavgFile -Force }
& $ff -y -hwaccel cuda -sseof -0.3 -i $tmpout -an -vf "signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=yavg$NN.txt" -f null - 2>$null
$yavg = -1.0
if (Test-Path -LiteralPath $yavgFile) {
  $m = Select-String -LiteralPath $yavgFile -Pattern "YAVG=([\d.]+)" | Select-Object -Last 1
  if ($m) { $yavg = [double]$m.Matches[0].Groups[1].Value }
}
$yavgOK = ($yavg -ge 14.5 -and $yavg -le 22)
"QC YAVG(lastframe): $yavg " + $(if ($yavgOK) { "OK" } else { "FAIL" })

# ---- 3. ebur128 loudness ----
$eb = & $ff -i $tmpout -map 0:a -af ebur128=peak=true -f null - 2>&1 | Out-String
$Im = [regex]::Matches($eb, "I:\s+(-?\d+\.\d+)\s*LUFS") | Select-Object -Last 1
$I = -99.0
if ($Im) { $I = [double]$Im.Groups[1].Value }
$loudOK = [math]::Abs($I + 14) -le 0.6
"QC loudness I=$([math]::Round($I,2)) LUFS " + $(if ($loudOK) { "OK" } else { "FIX NEEDED" })

if (-not $loudOK) {
  # two-pass loudnorm remux
  "  -> two-pass loudnorm remux for $NN ..."
  $p1 = & $ff -i $tmpout -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | Out-String
  # extract LAST JSON block containing input_i
  $jm = [regex]::Matches($p1, '\{[\s\S]*?\}') | Where-Object { $_.Value -match 'input_i' } | Select-Object -Last 1
  if (-not $jm) { throw "loudnorm pass1 JSON not found" }
  $j = $jm.Value | ConvertFrom-Json
  if ([string]::IsNullOrEmpty([string]$j.input_i)) { throw "loudnorm pass1 input_i empty" }
  $af = "loudnorm=I=-14:TP=-1:LRA=11:measured_I=$($j.input_i):measured_TP=$($j.input_tp):measured_LRA=$($j.input_lra):measured_thresh=$($j.input_thresh):offset=$($j.target_offset):linear=true"
  $remux = "$proj\clips\${NN}_$($w.slug)_ln.mp4"
  & $ff -y -i $tmpout -c:v copy -af $af -c:a aac -b:a 192k -ar 48000 -movflags +faststart $remux 2>$null
  if ($LASTEXITCODE -ne 0) { throw "loudnorm remux failed (exit $LASTEXITCODE)" }
  Move-Item -LiteralPath $remux -Destination $tmpout -Force
  # re-check
  $eb2 = & $ff -i $tmpout -map 0:a -af ebur128=peak=true -f null - 2>&1 | Out-String
  $I2 = [double]([regex]::Matches($eb2, "I:\s+(-?\d+\.\d+)\s*LUFS") | Select-Object -Last 1).Groups[1].Value
  $loudOK = [math]::Abs($I2 + 14) -le 0.6
  $I = $I2
  "  -> after remux I=$([math]::Round($I2,2)) " + $(if ($loudOK) { "OK" } else { "STILL FAIL" })
}

if ($fail.Count -gt 0 -or -not $yavgOK -or -not $loudOK) {
  throw "QC FAILED for $NN"
}

# ---- 4. thumbnails: REMOVED by extended user directive 2026-09-23 — no generated images at all ----

# ---- 5. qc composite: REMOVED by user directive 2026-09-23 — deliverable folders hold only shorts ----

# ---- 6. archive ass ----
Copy-Item -LiteralPath "D:\youtube system\output\temp\$NN.ass" -Destination "$proj\ass\${NN}_$($w.slug).ass" -Force

# ---- 7. metadata ----
$hook = (Get-Content -LiteralPath "D:\youtube system\output\temp\hooks_g3\$NN.txt" -Raw -Encoding UTF8).Trim()
$meta = @"
clip: $NN
slug: $($w.slug)
source: I Survived The Most Extreme Places On Earth [gTKS8SAwUzE]
window: $($w.s) -> $($w.e)  (dur $DUR s)
hook: $hook
video: h264_nvenc 1080x1920 yuv420p avg_frame_rate=30000/1001 cq18 p5 (GPU, software AV1 decode)
audio: aac 192k 48000Hz loudnorm I=-14 TP=-1 LRA=11 (I=$([math]::Round($I,2)) LUFS measured)
duration: $([math]::Round($cdur,2)) s (window $DUR)
size: $size bytes
YAVG last frame: $yavg
captions: Montserrat Bold 96px mixed case word-pop yellow (caption-styles.md v2.3), ass archived
pill: hook_pill.png overlay t=0..5 + hook title drawtext
fade: video in 0.3 / out 1 (st=$([math]::Round($DUR-1,3))), audio in 0.3 / out 0.5 (st=$([math]::Round($DUR-0.5,3)))
QC: PASS
"@
[System.IO.File]::WriteAllText("$proj\metadata\$NN.txt", $meta, (New-Object System.Text.UTF8Encoding($false)))

# ---- 8. per-clip temp cleanup ----
Remove-Item "D:\youtube system\output\temp\qcfr_$NN*.jpg" -Force -ErrorAction SilentlyContinue
Remove-Item "D:\youtube system\output\temp\yavg$NN.txt" -Force -ErrorAction SilentlyContinue
Remove-Item "D:\youtube system\output\temp\enc$NN.log" -Force -ErrorAction SilentlyContinue
Remove-Item "D:\youtube system\yavg*.txt" -Force -ErrorAction SilentlyContinue
Remove-Item "D:\youtube system\qcfr_*.jpg" -Force -ErrorAction SilentlyContinue

"QC PASS $NN : dur=$([math]::Round($cdur,2)) size=$size YAVG=$yavg I=$([math]::Round($I,2))"
