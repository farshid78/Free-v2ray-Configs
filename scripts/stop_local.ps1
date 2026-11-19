<#
.SYNOPSIS
  نمونه‌های محلیِ همین پروژه (وب‌سرور 8123 و ربات) را می‌بندد.

.DESCRIPTION
  فقط فرآیندهای پایتونی را می‌بندد که از همین مخزن اجرا شده‌اند:
    python -X utf8 -m http.server ... --directory <repo>
    python -X utf8 -m bot.main
  هر فرآیند دیگری (از جمله وابستگی‌های ویندوز/پروکسی) دست‌نخورده می‌ماند.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\stop_local.ps1
#>
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$rootPattern = [regex]::Escape($root)
$killed = @()

# لانچرها هم بسته می‌شوند؛ وگرنه watch-loop دوباره سرویس‌ها را بالا می‌آورد.
$launchers = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -ErrorAction SilentlyContinue
foreach ($lp in $launchers) {
    if ($lp.ProcessId -eq $PID) { continue }
    if ($lp.CommandLine -and $lp.CommandLine -match 'run_local\.ps1') {
        try {
            Stop-Process -Id $lp.ProcessId -Force -ErrorAction Stop
            $killed += [int]$lp.ProcessId
        } catch { }
    }
}

$procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue
foreach ($pr in $procs) {
    $cl = $pr.CommandLine
    if (-not $cl) { continue }
    # `--directory .` یعنی همین ریشه (مسیر مطلق در command line نیست).
    $isHttp = ($cl -match '-m\s+http\.server') -and
              (($cl -match $rootPattern) -or ($cl -match '--directory\s+(\."?|"?\.)'))
    $isBot = ($cl -match '-m\s+bot\.main') -and
             (($cl -match $rootPattern) -or ($cl -match '-X\s+utf8\s+-m\s+bot\.main'))
    if ($isHttp -or $isBot) {
        try {
            Stop-Process -Id $pr.ProcessId -Force -ErrorAction Stop
            $killed += [int]$pr.ProcessId
        } catch { }
    }
}

if ($killed.Count) {
    Write-Host ("[ok] stopped: " + ($killed -join ', ')) -ForegroundColor Green
} else {
    Write-Host "[ok] nothing was running for this project."
}
exit 0
