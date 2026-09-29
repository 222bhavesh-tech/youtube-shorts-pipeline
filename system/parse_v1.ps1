$log='C:\Users\bhavesh jeengar\.local\share\opencode\log\opencode.log'
$lines = Get-Content $log
$T = @{}
function W($nn){ if(-not $T[$nn]){$T[$nn]=@{nn=$nn}}; return $T[$nn] }
$rowLines = @()
foreach($l in $lines){
  # a) build spawns: $nn='NN'; $start=..; $dur=..; $end=..
  $m=[regex]::Matches($l, "\`$nn='(\d{2})'; \`$start=([0-9.]+); \`$dur=([0-9.]+); \`$end=([0-9.]+)")
  foreach($x in $m){
    $h = W $x.Groups[1].Value
    $h.start=$x.Groups[2].Value; $h.dur=$x.Groups[3].Value; $h.end=$x.Groups[4].Value
    $hk=[regex]::Match($l, "\`$hook='([^']*)'")
    if($hk.Success -and $hk.Groups[1].Value){ $h.hook=$hk.Groups[1].Value }
  }
  # b) QC slug: $nn='NN'; $slug='xxx'
  $s1=[regex]::Matches($l, "\`$nn='(\d{2})'; \`$slug='([^']+)'")
  foreach($x in $s1){ (W $x.Groups[1].Value).slug = $x.Groups[2].Value }
  # c) ass archive Move-Item NN.ass -> NN_slug.ass
  $s2=[regex]::Matches($l, 'Move-Item.{0,80}?(\d{2})\.ass.{0,80}?(\d{2})_([A-Za-z0-9_-]+)\.ass')
  foreach($x in $s2){ (W $x.Groups[1].Value).slug = $x.Groups[3].Value }
  # d) metadata rows
  if($l -match '\$rows = @\('){ $rowLines += 0 }
  $r=[regex]::Matches($l, "\@{nn='(\d{2})';slug='([^']*)'")
  foreach($x in $r){
    $h = W $x.Groups[1].Value
    if($x.Groups[2].Value){ $h.slug = $x.Groups[2].Value }
    # grab start/end/hook within this row object (row ends at next @{ or closing)
    $segStart = $x.Index
    $seg = $l.Substring($segStart, [math]::Min(2000, $l.Length-$segStart))
    $ms=[regex]::Match($seg, "start='([0-9.]+)'"); if($ms.Success){$h.mstart=$ms.Groups[1].Value}
    $me=[regex]::Match($seg, "end='([0-9.]+)'");   if($me.Success){$h.mend=$me.Groups[1].Value}
    $mh=[regex]::Match($seg, "hook='([^']*)'");    if($mh.Success -and $mh.Groups[1].Value){$h.hook=$mh.Groups[1].Value}
  }
}
# report
$out = 1..16 | ForEach-Object {
  $nn = '{0:d2}' -f $_
  $h = $T[$nn]
  if(-not $h){ [pscustomobject]@{nn=$nn; start='MISS'; end='MISS'; dur='MISS'; slug='MISS'; hook='MISS'} ; continue }
  $start = if($h.start){$h.start}else{$h.mstart}
  $end   = if($h.end){$h.end}else{$h.mend}
  $dur = if($start -and $end){[math]::Round([double]$end-[double]$start,3)}else{$h.dur}
  [pscustomobject]@{nn=$nn; start=$start; end=$end; dur=$dur; slug=$h.slug; hook=$h.hook}
}
$out | Format-Table -AutoSize | Out-String -Width 250 | Write-Output
Write-Output "rows-cmd chunks found in log (count): $($rowLines.Count)"
# how many distinct video-1 spawn lines total
$spawnCount = ($lines | Where-Object { $_ -match "\`$nn='(\d{2})'; \`$start=" }).Count
Write-Output "spawn lines: $spawnCount"
