$projects = @(
  @{ name = 'VIDEO-1 (I Stranded 100 People...)'; dir = 'D:\youtube system\output\final clips\extreme\en\I Stranded 100 People' },
  @{ name = 'VIDEO-2 (7 Days Underground City)'; dir = 'D:\youtube system\output\final clips\extreme\en\7 Days Underground City' },
  @{ name = 'VIDEO-3 (I Survived Extreme Places)'; dir = 'D:\youtube system\output\final clips\extreme\en\I Survived Extreme Places' }
)
$grand = 0; $grandPass = 0
foreach ($p in $projects) {
  ""
  "==== $($p.name)"
  "clips dir: $($p.dir)\clips"
  $mp4s = @(Get-ChildItem -LiteralPath "$($p.dir)\clips" -Filter *.mp4)
  $mds = @(Get-ChildItem -LiteralPath "$($p.dir)\metadata" -Filter *.txt | Sort-Object Name)
  $vpass = 0
  foreach ($m in $mds) {
    $t = Get-Content -LiteralPath $m.FullName -Raw
    $clip = '?'
    if ($t -match '(?m)^clip:\s*(\S+)') { $clip = $Matches[1] }
    $dur = '?'
    if ($t -match 'window:\s*([\d.]+)\s*->\s*([\d.]+)') {
      $dur = [math]::Round(([double]$Matches[2] - [double]$Matches[1]), 3)
    } elseif ($t -match '(?m)^duration:\s*([\d.]+)') { $dur = $Matches[1] }
    $yavg = '?'
    if ($t -match 'YAVG[^:\r\n]*:\s*(-?[\d.]+)') { $yavg = $Matches[1] }
    $I = '?'
    $im = [regex]::Matches($t, 'I=(-?[\d.]+)\s*LUFS')
    if ($im.Count -gt 0) { $I = $im[$im.Count - 1].Groups[1].Value }
    $szMB = '?'
    if ($t -match '(?m)^size:\s*(\d+)\s*bytes') { $szMB = [math]::Round([double]$Matches[1] / 1MB, 1) }
    $qc = 'FAIL'
    if ($t -match 'QC:\s*PASS') { $qc = 'PASS'; $vpass++ }
    $base = [IO.Path]::GetFileNameWithoutExtension($m.Name)
    $hit = $mp4s | Where-Object { $_.Name -eq "$base.mp4" -or $_.Name -like "${base}_*.mp4" } | Select-Object -First 1
    $file = if ($hit) { $hit.Name } else { '*** MP4 MISSING ***' }
    "  $clip | $dur s | YAVG $yavg | I $I | $szMB MB | $qc | $file"
  }
  "  => $($mds.Count) clips, QC PASS $vpass/$($mds.Count), mp4 on disk $($mp4s.Count)"
  $grand += $mds.Count; $grandPass += $vpass
}
""
"==== GRAND TOTAL: $grandPass/$grand QC PASS"
