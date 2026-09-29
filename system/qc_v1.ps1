param([string]$NN)
$ErrorActionPreference = "Continue"
$env:CUDA_VISIBLE_DEVICES = $null   # opencode server env may still carry -1 (GPU hidden)
$ffp = "D:\FunClip\tools\ffmpeg\bin\ffprobe.exe"
$ff  = "C:\Users\bhavesh jeengar\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"
Set-Location "D:\youtube system\output\temp"   # relative metadata=print:file= must land in temp, NOT root

$wins = @{
 "01"=@{s=0.0;      e=78.55;    slug="hook_final"; assn="01_hook.ass"}
 "02"=@{s=96.799;   e=175.239;  slug="no-shelter"}
 "03"=@{s=176.239;  e=252.68;   slug="living-kings"}
 "04"=@{s=470.8;    e=546.8;    slug="six-hour-shelter"}
 "05"=@{s=253.68;   e=329.68;   slug="wasted-everything"}
 "06"=@{s=620.64;   e=698.839;  slug="can-drop"}
 "07"=@{s=940.079;  e=1015.8;   slug="43-cans"}
 "08"=@{s=1016.32;  e=1093.32;  slug="results-reveal"}
 "09"=@{s=699.839;  e=775.5;    slug="storm-3am"}
 "10"=@{s=776.32;   e=852.44;   slug="tent-gone"}
 "11"=@{s=853.44;   e=930.44;   slug="frost-blankets"}
 "12"=@{s=1308.48;  e=1400.0;   slug="one-box"}
 "13"=@{s=1470.48;  e=1547.48;  slug="steak-nothing"}
 "14"=@{s=1618.159; e=1704.12;  slug="tarp-war"}
 "15"=@{s=1705.12;  e=1782.12;  slug="tears"}
 "16"=@{s=2139.599; e=2220.013; slug="winner-shelter"}
}
if (-not $wins.ContainsKey($NN)) { throw "unknown clip $NN" }
$w = $wins[$NN]
$DUR = [math]::Round($w.e - $w.s, 3)

$proj   = 'D:\youtube system\output\final clips\extreme\en\I Stranded 100 People'
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

# ---- 2. TRUE last-frame YAVG: decode final 0.3s (-sseof), take LAST frame ----
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
  $jm = [regex]::Matches($p1, '\{[\s\S]*?\}') | Where-Object { $_.Value -match 'input_i' } | Select-Object -Last 1
  if (-not $jm) { throw "loudnorm pass1 JSON not found" }
  $j = $jm.Value | ConvertFrom-Json
  if ([string]::IsNullOrEmpty([string]$j.input_i)) { throw "loudnorm pass1 input_i empty" }
  $af = "loudnorm=I=-14:TP=-1:LRA=11:measured_I=$($j.input_i):measured_TP=$($j.input_tp):measured_LRA=$($j.input_lra):measured_thresh=$($j.input_thresh):offset=$($j.target_offset):linear=true"
  $remux = "$proj\clips\${NN}_$($w.slug)_ln.mp4"
  & $ff -y -i $tmpout -c:v copy -af $af -c:a aac -b:a 192k -ar 48000 -movflags +faststart $remux 2>$null
  if ($LASTEXITCODE -ne 0) { throw "loudnorm remux failed (exit $LASTEXITCODE)" }
  Move-Item -LiteralPath $remux -Destination $tmpout -Force
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
# ---- 5. qc composite: REMOVED by user directive 2026-09-23 ----

# ---- 6. archive ass ----
$assn = if ($w.ContainsKey('assn')) { $w.assn } else { "${NN}_$($w.slug).ass" }
Copy-Item -LiteralPath "D:\youtube system\output\temp\v1ass\$NN.ass" -Destination "$proj\ass\$assn" -Force

# ---- 7. metadata ----
$hook = (Get-Content -LiteralPath "D:\youtube system\output\temp\hooks_v1\$NN.txt" -Raw -Encoding UTF8).Trim()
$meta = @"
clip: $NN
slug: $($w.slug)
source: I Stranded 100 People In The Wilderness For `$250,000
window: $($w.s) -> $($w.e)  (dur $DUR s)
hook: $hook
video: h264_nvenc 1080x1920 yuv420p avg_frame_rate=30000/1001 cq18 p5 (GPU)
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
