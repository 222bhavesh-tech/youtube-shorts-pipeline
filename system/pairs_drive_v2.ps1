# Video-2 rebuild driver: ALL 13 clips. PAIRS (2 concurrent GPU encodes),
# QC both members of a pair in parallel, then next pair. Clip 13 solo.
$ErrorActionPreference = 'Continue'
Set-Location "D:\youtube system\output\temp"
$proj = 'D:\youtube system\output\final clips\extreme\en\7 Days Underground City'

function Run-Two([int[]]$nns, [string]$script) {
    $procs = @()
    foreach ($nn in $nns) {
        $id = "{0:d2}" -f $nn
        $procs += ,@($nn, (Start-Process -FilePath "powershell" `
            -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',"D:\youtube system\system\$script",'-NN',$id) `
            -PassThru -NoNewWindow `
            -RedirectStandardOutput "D:\youtube system\output\temp\pair_${script}_$id.out" `
            -RedirectStandardError  "D:\youtube system\output\temp\pair_${script}_$id.err"))
    }
    $codes = @()
    foreach ($p in $procs) {
        $proc = $p[1]; $nn = $p[0]
        $proc.WaitForExit()
        $code = $proc.ExitCode
        $codes += ,@($nn, $code)
        Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} {1} nn={2} exit={3}" -f (Get-Date -Format 'HH:mm:ss'), $script, ("{0:d2}" -f $nn), $code)
    }
    return $codes
}

# deterministic full rebuild: clear prior outputs of THIS project only
Remove-Item "$proj\clips\*.mp4" -Force -ErrorAction SilentlyContinue
Remove-Item "$proj\metadata\*.txt" -Force -ErrorAction SilentlyContinue

Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} V2 DRIVER START pairs 01/02 03/04 05/06 07/08 09/10 11/12 solo 13" -f (Get-Date -Format 'HH:mm:ss'))

$pairs = @(@(1,2), @(3,4), @(5,6), @(7,8), @(9,10), @(11,12))
foreach ($p in $pairs) {
    $tag = ($p -join '+')
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} V2 ENCODE PAIR START {1}" -f (Get-Date -Format 'HH:mm:ss'), $tag)
    $enc = Run-Two $p 'build_new.ps1'
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} V2 ENCODE PAIR DONE {1} codes={2}" -f (Get-Date -Format 'HH:mm:ss'), $tag, (($enc | ForEach-Object { "$($_[0]):$($_[1])" }) -join ' '))
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} V2 QC PAIR START {1}" -f (Get-Date -Format 'HH:mm:ss'), $tag)
    $qc = Run-Two $p 'qc_new.ps1'
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} V2 QC PAIR DONE {1} codes={2}" -f (Get-Date -Format 'HH:mm:ss'), $tag, (($qc | ForEach-Object { "$($_[0]):$($_[1])" }) -join ' '))
}

Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} V2 ENCODE SOLO START 13" -f (Get-Date -Format 'HH:mm:ss'))
$enc13 = Run-Two @(13) 'build_new.ps1'
Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} V2 ENCODE SOLO DONE 13 codes={1}" -f (Get-Date -Format 'HH:mm:ss'), (($enc13 | ForEach-Object { "$($_[0]):$($_[1])" }) -join ' '))
Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} V2 QC SOLO START 13" -f (Get-Date -Format 'HH:mm:ss'))
$qc13 = Run-Two @(13) 'qc_new.ps1'
Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} V2 QC SOLO DONE 13 codes={1}" -f (Get-Date -Format 'HH:mm:ss'), (($qc13 | ForEach-Object { "$($_[0]):$($_[1])" }) -join ' '))

# artifact verification (child exit codes unreliable) -> QC PASS count is the gate
$mp4 = @(Get-ChildItem "$proj\clips\*.mp4" -ErrorAction SilentlyContinue).Count
$pass = @(Get-ChildItem "$proj\metadata\*.txt" -ErrorAction SilentlyContinue | Where-Object { (Get-Content $_.FullName -Raw) -match 'QC: PASS' }).Count
Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} V2 VERIFY clips={1}/13 qc_pass={2}/13" -f (Get-Date -Format 'HH:mm:ss'), $mp4, $pass)
if ($mp4 -eq 13 -and $pass -eq 13) {
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} V2 DRIVER ALL DONE" -f (Get-Date -Format 'HH:mm:ss'))
    exit 0
} else {
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} V2 DRIVER DONE WITH FAILURES" -f (Get-Date -Format 'HH:mm:ss'))
    exit 1
}
