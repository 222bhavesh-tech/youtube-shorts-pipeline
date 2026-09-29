# Pair-parallel driver for video 3: encodes clips 01-14 in PAIRS (2 encodes
# concurrently on the GPU), QC's both members of a pair in parallel, then
# moves to the next pair. 14 clips = 7 full pairs, no solo.
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

Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} G3 DRIVER START pairs 01/02 03/04 05/06 07/08 09/10 11/12 13/14" -f (Get-Date -Format 'HH:mm:ss'))

$pairs = @(@(1,2), @(3,4), @(5,6), @(7,8), @(9,10), @(11,12), @(13,14))
foreach ($p in $pairs) {
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} ENCODE PAIR START {1}" -f (Get-Date -Format 'HH:mm:ss'), ($p -join '+'))
    $enc = Run-Two $p 'build_g3.ps1'
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} ENCODE PAIR DONE {1} codes={2}" -f (Get-Date -Format 'HH:mm:ss'), ($p -join '+'), (($enc | ForEach-Object { "$($_[0]):$($_[1])" }) -join ' '))
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} QC PAIR START {1}" -f (Get-Date -Format 'HH:mm:ss'), ($p -join '+'))
    $qc  = Run-Two $p 'qc_g3.ps1'
    Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} QC PAIR DONE {1} codes={2}" -f (Get-Date -Format 'HH:mm:ss'), ($p -join '+'), (($qc | ForEach-Object { "$($_[0]):$($_[1])" }) -join ' '))
}

Add-Content -Path "D:\youtube system\output\temp\driver.log" -Value ("{0} G3 DRIVER ALL DONE" -f (Get-Date -Format 'HH:mm:ss'))
Write-Output "G3 DRIVER ALL DONE - see D:\youtube system\output\temp\driver.log"
