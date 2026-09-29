param([string]$NN)
$ErrorActionPreference = "Stop"
$env:CUDA_VISIBLE_DEVICES = $null   # opencode server env may still carry -1 (GPU hidden)
$wins = @{
 "01"=@{s=2.750;   e=80.447;  slug="400ft_underground"}
 "02"=@{s=82.630;  e=191.858; slug="whos_coming_next"}
 "03"=@{s=232.680; e=315.248; slug="1000_year_tunnel"}
 "04"=@{s=317.670; e=392.792; slug="ominous_staircase"}
 "05"=@{s=394.909; e=475.441; slug="kai_cenat_cave"}
 "06"=@{s=478.629; e=556.156; slug="lights_off_prank"}
 "07"=@{s=557.190; e=634.133; slug="mannequin_prank"}
 "08"=@{s=635.150; e=711.578; slug="bed_in_water"}
 "09"=@{s=711.750; e=788.154; slug="longest_tunnel"}
 "10"=@{s=863.310; e=946.780; slug="underground_coup"}
 "11"=@{s=952.749; e=1046.979;slug="giant_box_surprise"}
 "12"=@{s=1049.950;e=1126.692;slug="underground_soccer"}
 "13"=@{s=1128.270;e=1234.900;slug="ten_second_drop"}
}
if (-not $wins.ContainsKey($NN)) { throw "unknown clip $NN" }
$w = $wins[$NN]
$DUR = [math]::Round($w.e - $w.s, 3)
$vfade = [math]::Round($DUR - 1, 3)
$afade = [math]::Round($DUR - 0.5, 3)

Set-Location "D:\youtube system\output\temp"
Copy-Item "D:\youtube system\output\temp\hooks_new\$NN.txt" "D:\youtube system\output\temp\hook$NN.txt" -Force

$Expr = (Get-Content -LiteralPath "D:\youtube system\output\face_track\en\7 Days Underground City_crop$NN.txt" -Raw).Trim()
$Enable = (Get-Content -LiteralPath "D:\youtube system\output\face_track\en\7 Days Underground City_track$NN.json" -Raw | ConvertFrom-Json).enable_expr

$fc = @"
[0:v]split=3[v0][v1][v2];
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

$src = "D:\youtube system\output\4k video\en\7 Days Exploring An Underground City [bn0Kh9c4Zv4].mp4"
$pill = "D:\youtube system\system\assets\hook_pill.png"
$out = "D:\youtube system\output\final clips\extreme\en\7 Days Underground City\clips\${NN}_$($w.slug).mp4"
$ff7 = "C:\Users\bhavesh jeengar\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"

# GPU path: NVDEC (cuda) decode + h264_nvenc CQ18 encode (ffmpeg 7.1.1 = NVENC API 13.0)
$ErrorActionPreference = "Continue"
& $ff7 -y -hwaccel cuda -ss $w.s -t $DUR -i $src -i $pill -filter_complex $fc -map "[v]" -map "[a]" `
  -c:v h264_nvenc -preset p5 -rc vbr -cq 18 -b:v 0 -spatial-aq 1 -c:a aac -b:a 192k -ar 48000 `
  -movflags +faststart -pix_fmt yuv420p $out 2> "D:\youtube system\output\temp\enc$NN.log"
$encCode = $LASTEXITCODE
$ErrorActionPreference = "Stop"
if ($encCode -ne 0) {
  $tail = (Get-Content "D:\youtube system\output\temp\enc$NN.log" -Tail 8 -ErrorAction SilentlyContinue) -join "`n"
  throw "ffmpeg failed for $NN (exit $encCode):`n$tail"
}
"ENCODED $NN start=$($w.s) dur=$DUR -> $out"
