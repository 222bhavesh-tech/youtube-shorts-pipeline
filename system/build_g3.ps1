param([string]$NN)
$ErrorActionPreference = "Stop"
$env:CUDA_VISIBLE_DEVICES = $null   # opencode server env may still carry -1 (GPU hidden)
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
$vfade = [math]::Round($DUR - 1, 3)
$afade = [math]::Round($DUR - 0.5, 3)

Set-Location "D:\youtube system\output\temp"
Copy-Item "D:\youtube system\output\temp\hooks_g3\$NN.txt" "D:\youtube system\output\temp\hook$NN.txt" -Force

$Expr = (Get-Content -LiteralPath "D:\youtube system\output\face_track\en\I Survived Extreme Places_crop$NN.txt" -Raw).Trim()
$Enable = (Get-Content -LiteralPath "D:\youtube system\output\face_track\en\I Survived Extreme Places_track$NN.json" -Raw | ConvertFrom-Json).enable_expr

# video-3 source is AV1 4K (no NVDEC AV1 on P620) -> software decode,
# prepend scale=1920:1080 so crop coords match face_track proxy geometry
$fc = @"
[0:v]scale=1920:1080[sv];
[sv]split=3[v0][v1][v2];
[v0]crop=608:1080:x='$Expr':y=0,scale=1080:1920:flags=lanczos[fa];
[v1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.25[fb];
[v2]scale=1080:864:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:864[fg];
[fb][fg]overlay=0:384[wide];
[wide][fa]overlay=0:0:enable='$Enable'[mix];
[mix]ass='$NN.ass'[sub];
[1:v]format=rgba[pill];
[sub][pill]overlay=0:84:enable='between(t,0,5)'[hooked];
[hooked]drawtext=fontfile='fonts/montserrat-bold.ttf':textfile='hook$NN.txt':fontcolor=black:fontsize=40:x='(W-text_w)/2':y='84+(120-text_h)/2':enable='between(t,0,5)'[txt];
[txt]fade=t=in:st=0:d=0.3,fade=t=out:st=${vfade}:d=1,fps=30000/1001[v];
[0:a]loudnorm=I=-14:TP=-1:LRA=11,afade=t=in:st=0:d=0.3,afade=t=out:st=${afade}:d=0.5[a]
"@

$src = "D:\youtube system\output\4k video\en\I Survived The Most Extreme Places On Earth [gTKS8SAwUzE].webm"
$pill = "D:\youtube system\system\assets\hook_pill.png"
$out = "D:\youtube system\output\final clips\extreme\en\I Survived Extreme Places\clips\${NN}_$($w.slug).mp4"
$ff7 = "C:\Users\bhavesh jeengar\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"

# GPU encode path: software AV1 (dav1d) decode + h264_nvenc CQ18 encode — NO -hwaccel cuda (P620 NVDEC has no AV1)
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
