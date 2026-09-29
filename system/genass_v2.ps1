# Regenerate video-2 ASS captions (13) into temp\NN.ass using plain_bn0 transcript.
$ErrorActionPreference = 'Stop'
Set-Location 'D:\youtube system\output\temp'
$py = 'C:\Users\bhavesh jeengar\AppData\Local\Programs\Python\Python312\python.exe'
$tr = 'D:\youtube system\output\transcript\en\plain_bn0.txt'
$wins = [ordered]@{
 '01'=@(2.750,80.447);    '02'=@(82.630,191.858);   '03'=@(232.680,315.248)
 '04'=@(317.670,392.792); '05'=@(394.909,475.441);  '06'=@(478.629,556.156)
 '07'=@(557.190,634.133); '08'=@(635.150,711.578);  '09'=@(711.750,788.154)
 '10'=@(863.310,946.780); '11'=@(952.749,1046.979); '12'=@(1049.950,1126.692)
 '13'=@(1128.270,1234.900)
}
foreach ($k in $wins.Keys) {
  $a = $wins[$k]
  & $py 'D:\youtube system\system\gen_ass.py' $a[0] $a[1] "$k.ass" $tr
  if ($LASTEXITCODE -ne 0) { throw "gen_ass $k failed" }
  $len = (Get-Item -LiteralPath "$k.ass").Length
  Write-Output "ass $k $([math]::Round($a[1]-$a[0],3))s -> $len bytes"
}
'GENASS V2 DONE'
