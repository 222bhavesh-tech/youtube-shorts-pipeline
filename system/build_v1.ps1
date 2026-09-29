param([string]$NN)
$ErrorActionPreference = "Stop"
$env:CUDA_VISIBLE_DEVICES = $null   # opencode server env may still carry -1 (GPU hidden)
$wins = @{
 "01"=@{s=0.0;      e=78.55;    slug="hook_final"}
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
$vfade = [math]::Round($DUR - 1, 3)
$afade = [math]::Round($DUR - 0.5, 3)

Set-Location "D:\youtube system\output\temp"
if (-not (Test-Path -LiteralPath "D:\youtube system\output\temp\v1ass\$NN.ass")) { throw "missing v1ass\$NN.ass (run genass_v1.ps1 first)" }
Copy-Item "D:\youtube system\output\temp\hooks_v1\$NN.txt" "D:\youtube system\output\temp\hook$NN.txt" -Force

if ($NN -eq "01") {
  $cropFile = "D:\youtube system\output\face_track\en\I Stranded 100 People_crop_test.txt"
  $trackFile = "D:\youtube system\output\face_track\en\I Stranded 100 People_track.json"
} else {
  $cropFile = "D:\youtube system\output\face_track\en\I Stranded 100 People_crop$NN.txt"
  $trackFile = "D:\youtube system\output\face_track\en\I Stranded 100 People_track$NN.json"
}
$Expr = (Get-Content -LiteralPath $cropFile -Raw).Trim()
$Enable = (Get-Content -LiteralPath $trackFile -Raw | ConvertFrom-Json).enable_expr
if ([string]::IsNullOrWhiteSpace($Enable)) { throw "empty enable_expr for $NN" }

# video-1 source: 1080p VP9 (odd container avg_frame_rate) -> software decode,
# explicit fps=30000/1001 in fade chain (QC requires exact avg_frame_rate)
$fc = @"
[0:v]split=3[v0][v1][v2];
[v0]crop=608:1080:x='$Expr':y=0,scale=1080:1920:flags=lanczos[fa];
[v1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.25[fb];
[v2]scale=1080:864:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:864[fg];
[fb][fg]overlay=0:384[wide];
[wide][fa]overlay=0:0:enable='$Enable'[mix];
[mix]ass='v1ass/$NN.ass'[sub];
[1:v]format=rgba[pill];
[sub][pill]overlay=0:84:enable='between(t,0,5)'[hooked];
[hooked]drawtext=fontfile='fonts/montserrat-bold.ttf':textfile='hook$NN.txt':fontcolor=black:fontsize=40:x='(W-text_w)/2':y='84+(120-text_h)/2':enable='between(t,0,5)'[txt];
[txt]fade=t=in:st=0:d=0.3,fade=t=out:st=${vfade}:d=1,fps=30000/1001[v];
[0:a]loudnorm=I=-14:TP=-1:LRA=11,afade=t=in:st=0:d=0.3,afade=t=out:st=${afade}:d=0.5[a]
"@

$src = 'D:\youtube system\output\4k video\en\I Stranded 100 People In The Wilderness For $250,000.mp4'
$pill = 'D:\youtube system\system\assets\hook_pill.png'
$proj = 'D:\youtube system\output\final clips\extreme\en\I Stranded 100 People'
$out = "$proj\clips\${NN}_$($w.slug).mp4"
$ff7 = "C:\Users\bhavesh jeengar\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"

foreach ($d in @('clips','ass','metadata')) { New-Item -ItemType Directory -Force -Path "$proj\$d" | Out-Null }

# GPU encode path: software VP9 decode + h264_nvenc CQ18 encode (NO -hwaccel cuda: VP9 NVDEC unreliable on P620)
$ErrorActionPreference = "Continue"
& $ff7 -y -ss $w.s -t $DUR -i $src -i $pill -filter_complex $fc -map "[v]" -map "[a]" `
  -c:v h264_nvenc -preset p5 -rc vbr -cq 18 -b:v 0 -spatial-aq 1 -c:a aac -b:a 192k -ar 48000 `
  -movflags +faststart -pix_fmt yuv420p $out 2> "D:\youtube system\output\temp\enc$NN.log"
$encCode = $LASTEXITCODE
$ErrorActionPreference = "Stop"
if ($encCode -ne 0) {
  $tail = (Get-Content "D:\youtube system\output\temp\enc$NN.log" -Tail 8 -ErrorAction SilentlyContinue) -join "`n"
  throw "ffmpeg failed for $NN (exit $encCode):`n$tail"
}
"ENCODED $NN start=$($w.s) dur=$DUR -> $out"
