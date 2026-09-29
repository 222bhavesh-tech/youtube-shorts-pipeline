# Generate video-1 ASS captions (16) into temp\v1ass\NN.ass using plain.txt (default transcript).
$ErrorActionPreference = 'Stop'
Set-Location 'D:\youtube system\output\temp'
New-Item -ItemType Directory -Force -Path 'D:\youtube system\output\temp\v1ass' | Out-Null
$py = 'C:\Users\bhavesh jeengar\AppData\Local\Programs\Python\Python312\python.exe'
$wins = [ordered]@{
 '01'=@(0.0,78.55);       '02'=@(96.799,175.239);   '03'=@(176.239,252.68)
 '04'=@(470.8,546.8);     '05'=@(253.68,329.68);    '06'=@(620.64,698.839)
 '07'=@(940.079,1015.8);  '08'=@(1016.32,1093.32);  '09'=@(699.839,775.5)
 '10'=@(776.32,852.44);   '11'=@(853.44,930.44);    '12'=@(1308.48,1400.0)
 '13'=@(1470.48,1547.48); '14'=@(1618.159,1704.12); '15'=@(1705.12,1782.12)
 '16'=@(2139.599,2220.013)
}
foreach ($k in $wins.Keys) {
  $a = $wins[$k]
  & $py 'D:\youtube system\system\gen_ass.py' $a[0] $a[1] "v1ass\$k.ass"
  if ($LASTEXITCODE -ne 0) { throw "gen_ass $k failed" }
  $len = (Get-Item -LiteralPath "v1ass\$k.ass").Length
  Write-Output "v1ass $k $([math]::Round($a[1]-$a[0],3))s -> $len bytes"
}
'GENASS V1 DONE'
