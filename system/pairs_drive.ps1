# Pair-parallel driver: encodes remaining clips 03-13 in PAIRS (2 encodes
# concurrently on the GPU), QC's both members of a pair in parallel, then
# moves to the next pair. Clip 13 runs solo (odd count).
$ErrorActionPreference = 'Continue'
Set-Location "D:\youtube system\output\temp"

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

Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} DRIVER START pairs 03/04 05/06 07/08 09/10 11/12 solo 13" -f (Get-Date -Format 'HH:mm:ss'))

$pairs = @(@(3,4), @(5,6), @(7,8), @(9,10), @(11,12))
foreach ($p in $pairs) {
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} ENCODE PAIR START {1}" -f (Get-Date -Format 'HH:mm:ss'), ($p -join '+'))
    $enc = Run-Two $p 'build_new.ps1'
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} ENCODE PAIR DONE {1} codes={2}" -f (Get-Date -Format 'HH:mm:ss'), ($p -join '+'), (($enc | ForEach-Object { "$($_[0]):$($_[1])" }) -join ' '))
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} QC PAIR START {1}" -f (Get-Date -Format 'HH:mm:ss'), ($p -join '+'))
    $qc  = Run-Two $p 'qc_new.ps1'
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} QC PAIR DONE {1} codes={2}" -f (Get-Date -Format 'HH:mm:ss'), ($p -join '+'), (($qc | ForEach-Object { "$($_[0]):$($_[1])" }) -join ' '))
}

Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} SOLO 13 ENCODE START" -f (Get-Date -Format 'HH:mm:ss'))
$s13 = Run-Two @(13) 'build_new.ps1'
Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} SOLO 13 ENCODE DONE codes={1}" -f (Get-Date -Format 'HH:mm:ss'), (($s13 | ForEach-Object { "$($_[0]):$($_[1])" }) -join ' '))
Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} SOLO 13 QC START" -f (Get-Date -Format 'HH:mm:ss'))
$q13 = Run-Two @(13) 'qc_new.ps1'
Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} SOLO 13 QC DONE codes={1}" -f (Get-Date -Format 'HH:mm:ss'), (($q13 | ForEach-Object { "$($_[0]):$($_[1])" }) -join ' '))

Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} DRIVER ALL DONE" -f (Get-Date -Format 'HH:mm:ss'))
Write-Output "DRIVER ALL DONE - see D:\youtube system\output\temp\driver.log"
