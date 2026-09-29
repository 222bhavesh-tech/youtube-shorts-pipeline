$proj = 'D:\youtube system\output\final clips\extreme\en\I Stranded 100 People'
$mp4 = @(Get-ChildItem -LiteralPath "$proj\clips" -Filter *.mp4)
$ass = @(Get-ChildItem -LiteralPath "$proj\ass" -Filter *.ass)
$md  = @(Get-ChildItem -LiteralPath "$proj\metadata" -Filter *.txt -ErrorAction SilentlyContinue)
$pass = @($md | Where-Object { (Get-Content $_.FullName -Raw) -match 'QC: PASS' })
"mp4: $($mp4.Count)/16"
"ass: $($ass.Count)/16"
"metadata: $($md.Count)/16"
"QC PASS: $($pass.Count)/16"
$sample = "$proj\metadata\01.txt"
if (Test-Path -LiteralPath $sample) { "--- sample 01.txt ---"; Get-Content -LiteralPath $sample }
