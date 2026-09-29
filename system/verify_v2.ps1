$proj = 'D:\youtube system\output\final clips\extreme\en\7 Days Underground City'
$mp4 = @(Get-ChildItem -LiteralPath "$proj\clips" -Filter *.mp4)
$ass = @(Get-ChildItem -LiteralPath "$proj\ass" -Filter *.ass)
$hk  = @(Get-ChildItem -LiteralPath "$proj\hooks" -Filter *.txt)
$md  = @(Get-ChildItem -LiteralPath "$proj\metadata" -Filter *.txt)
$pass = @($md | Where-Object { (Get-Content $_.FullName -Raw) -match 'QC: PASS' })
"mp4: $($mp4.Count)/13"
"ass: $($ass.Count)/13"
"hooks: $($hk.Count)/13"
"metadata: $($md.Count)/13"
"QC PASS: $($pass.Count)/13"
$totalGB = [math]::Round((($mp4 | Measure-Object Length -Sum).Sum / 1GB), 3)
"total size: $totalGB GB"
$mp4 | Sort-Object Name | ForEach-Object { "  $($_.Name)  $([math]::Round($_.Length/1MB,1)) MB" }
