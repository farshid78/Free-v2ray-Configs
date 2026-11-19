<#
.SYNOPSIS
  همهٔ سرویس‌های محلیِ Free-v2ray-Configs را با یک دستور بالا می‌آورد و تا Ctrl+C زنده نگه می‌دارد.

.DESCRIPTION
  سرویس‌ها:
    ۱) وب‌سرور ایستا:  python -X utf8 -m http.server <port> --bind 127.0.0.1 --directory .
       ▸ ریشهٔ مخزن سرو می‌شود (نه docs/)، چون داشبورد محلی index.json / health.json /
         Countries/index.json را از همان origin می‌خواند.
    ۲) ربات تلگرام:  python -X utf8 -m bot.main
       ▸ همان ماژولی که CI/مستندات می‌شناسد (bot/main.py با گارد __main__).
       ▸ واریابل‌های پروکسیِ محیط پاک می‌شوند؛ با env آلوده به پروکسی، long-poll
         ربات معلق می‌ماند و هیچ getUpdates نمی‌زند.

  لاگ‌ها در .cache/logs/ نوشته می‌شوند و هر بار از نو ساخته می‌شوند:
    local_http.log / local_http.err / local_bot.log / local_bot.err

.PARAMETER Port
  پورت وب‌سرور (پیش‌فرض 8123). اگر اشغال باشد، اسکریپت با پیام واضح می‌ایستد.

.PARAMETER NoBot
  فقط وب‌سرور را بالا بیاور.

.PARAMETER NoRestart
  اگر سرویسی از کار افتاد، دوباره بالا نیاور (پیش‌فرض: بالا آوردنِ دوباره).

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_local.ps1
.EXAMPLE
  scripts\run_local.ps1 -Port 8124 -NoBot
#>
param(
    [int]$Port = 8123,
    [switch]$NoBot,
    [switch]$NoRestart
)

$ErrorActionPreference = 'Stop'
# نوارِ پیشرفتِ Invoke-WebRequest در PowerShell 5.1 کنسول را شلوغ می‌کند.
$ProgressPreference = 'SilentlyContinue'

# ── ریشهٔ مخزن (این فایل در scripts/ است) ──────────────────────────────────────
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# ── python ────────────────────────────────────────────────────────────────────
$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) {
    Write-Host "ERROR: 'python' not found on PATH." -ForegroundColor Red
    exit 1
}
$pyExe = $py.Source

# ── پورت آزاد است؟ (پیش از دست‌زدن به لاگ‌ها، چون لاگ ممکن است قفل باشد) ───
function Get-PortOwner([int]$p) {
    try {
        $c = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction Stop |
             Select-Object -First 1
        if ($c) { return [int]$c.OwningProcess }
    } catch { }
    return 0
}

# ── نمونهٔ قبلیِ همین پروژه: جای خطا، تمیز جمع می‌شود ────────────────────────
# کاربر معمولاً دوبار روی start-local.cmd می‌زند؛ پیامِ «پورت اشغال است» در آن
# حالت درست نیست، چون مالکِ پورت خودِ همین پروژه است. پس اگر فرآیندِ صاحبِ پورت
# همان http.serverِ این مخزن بود، اول نمونهٔ قبلی را می‌بندیم و بعد بالا می‌آوریم.
function Get-CmdLine([int]$procId) {
    try {
        (Get-CimInstance Win32_Process -Filter "ProcessId=$procId" -ErrorAction Stop).CommandLine
    } catch { '' }
}

function Stop-OwnServices {
    $killed = @()
    # لانچرهای قبلی هم باید بروند، وگرنه watch-loop آن‌ها ربات را دوباره بالا
    # می‌آورد و دو instance هم‌زمان getUpdates می‌زنند (تلگرام 409 Conflict).
    $oldLaunchers = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -ErrorAction SilentlyContinue
    foreach ($lp in $oldLaunchers) {
        if ($lp.ProcessId -eq $PID) { continue }
        if ($lp.CommandLine -and $lp.CommandLine -match 'run_local\.ps1') {
            try {
                Stop-Process -Id $lp.ProcessId -Force -ErrorAction Stop
                $killed += [int]$lp.ProcessId
            } catch { }
        }
    }
    $procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue
    $rootPattern = [regex]::Escape($root)
    foreach ($pr in $procs) {
        $cl = $pr.CommandLine
        if (-not $cl) { continue }
        # http.server با `--directory .` از همین ریشه اجرا می‌شود، پس مسیر مطلق
        # در command line نیست؛ هر دو شکل پذیرفته می‌شوند.
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
    return $killed
}

$owner = Get-PortOwner $Port
if ($owner -ne 0) {
    $ownerCmd = Get-CmdLine $owner
    $isOwnServer = ($ownerCmd -match '-m\s+http\.server') -and
                   (($ownerCmd -match [regex]::Escape($root)) -or
                    ($ownerCmd -match '--directory\s+(\."?|"?\.)'))
    if ($isOwnServer) {
        Write-Host "[info] previous local instance found (PID $owner) - restarting it." -ForegroundColor Yellow
        $killed = Stop-OwnServices
        if ($killed.Count) { Write-Host ("[info] stopped: " + ($killed -join ', ')) }
        Start-Sleep -Seconds 2
        $owner = Get-PortOwner $Port
    }
    if ($owner -ne 0) {
        Write-Host "ERROR: port $Port is already in use by PID $owner." -ForegroundColor Red
        Write-Host "       it is not this project's server; stop it with:"
        Write-Host "         Stop-Process -Id $owner -Force      (or run: .\start-local.cmd -Port 8124)"
        Write-Host "       tip: .\stop-local.cmd stops only this project's instances."
        exit 1
    }
}

# ── لاگ‌ها ────────────────────────────────────────────────────────────────────
$logDir = Join-Path $root '.cache\logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Get-LogPath([string]$name) { Join-Path $logDir $name }

# python-logging پیش‌فرض روی stderr می‌نویسد، پس هر دو فایل با هم خوانده می‌شوند.
function Read-Log([string[]]$paths) {
    $t = ''
    foreach ($p in $paths) {
        if (Test-Path $p) { $t += (Get-Content -Raw -ErrorAction SilentlyContinue $p) }
    }
    return $t
}

$httpOut = Get-LogPath 'local_http.log'
$httpErr = Get-LogPath 'local_http.err'
$botOut  = Get-LogPath 'local_bot.log'
$botErr  = Get-LogPath 'local_bot.err'

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

# آیا می‌توان روی این فایل نوشت؟ (فایلی که پروسهٔ دیگری قفل کرده، رد می‌شود.)
function Test-Writable([string]$path) {
    try {
        $fs = [System.IO.File]::Open($path, [System.IO.FileMode]::Append,
                                     [System.IO.FileAccess]::Write,
                                     [System.IO.FileShare]::ReadWrite)
        $fs.Close()
        return $true
    } catch {
        return $false
    }
}

# لاگ هر سرویس: اگر مسیرِ پیش‌فرض قفل باشد، مسیرِ جایگزین با مهرِ زمان برمی‌گردد.
function Resolve-LogPath([string]$path) {
    if (Test-Writable $path) {
        try { [System.IO.File]::WriteAllText($path, '') } catch { }
        return $path
    }
    $dir  = [System.IO.Path]::GetDirectoryName($path)
    $name = [System.IO.Path]::GetFileNameWithoutExtension($path)
    $ext  = [System.IO.Path]::GetExtension($path)
    $alt  = Join-Path $dir ($name + '.' + $stamp + $ext)
    if (Test-Writable $alt) { return $alt }
    $tmp = Join-Path $env:TEMP ('f2c-' + $name + '.' + $stamp + $ext)
    Write-Host ("WARN: '{0}' is locked -> logs go to {1}" -f $path, $tmp) -ForegroundColor Yellow
    return $tmp
}

$httpOut = Resolve-LogPath $httpOut
$httpErr = Resolve-LogPath $httpErr
$botOut  = Resolve-LogPath $botOut
$botErr  = Resolve-LogPath $botErr

# ── توکن ربات ─────────────────────────────────────────────────────────────────
$startBot = -not $NoBot
if ($startBot) {
    $envFile = Join-Path $root '.env'
    $hasToken = $false
    if (Test-Path $envFile) {
        $hasToken = [bool](Select-String -Path $envFile -Pattern '^\s*BOT_TOKEN\s*=\s*\S+' -Quiet)
    }
    if (-not $hasToken) {
        Write-Host "WARN: BOT_TOKEN is empty/missing in .env -> bot will be skipped." -ForegroundColor Yellow
        $startBot = $false
    }
}

# پروکسی‌های محیطیِ خراب/دور، long-poll ربات را معلق می‌کنند؛ ولی پروکسیِ
# لوکال (127.0.0.1/localhost) همان کلاینت VPN کاربر است و باید بماند، وگرنه
# ربات در شبکه‌ای که تلگرام فیلتر است هرگز به api.telegram.org نمی‌رسد.
foreach ($v in 'HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy') {
    $val = [Environment]::GetEnvironmentVariable($v)
    if (-not $val) { continue }
    if ($val -match '(?i)(127\.0\.0\.1|localhost|\[::1\])') { continue }
    Remove-Item "Env:$v" -ErrorAction SilentlyContinue
}

# ── شروعِ سرویس‌ها ────────────────────────────────────────────────────────────
function Start-HttpServer {
    Start-Process -FilePath $pyExe `
        -ArgumentList '-X','utf8','-m','http.server',"$Port",'--bind','127.0.0.1','--directory','.' `
        -WorkingDirectory $root -WindowStyle Hidden `
        -RedirectStandardOutput $httpOut -RedirectStandardError $httpErr `
        -PassThru
}

function Start-Bot {
    Start-Process -FilePath $pyExe `
        -ArgumentList '-X','utf8','-m','bot.main' `
        -WorkingDirectory $root -WindowStyle Hidden `
        -RedirectStandardOutput $botOut -RedirectStandardError $botErr `
        -PassThru
}

$httpProc = Start-HttpServer
$botProc = $null
if ($startBot) { $botProc = Start-Bot }

# ── آمادگی: وب‌سرور باید /docs/ را ۲۰۰ بدهد ───────────────────────────────────
$url = "http://127.0.0.1:$Port/docs/"
$httpOk = $false
for ($i = 0; $i -lt 40; $i++) {
    Start-Sleep -Milliseconds 500
    if ($httpProc.HasExited) { break }
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3
        if ($r.StatusCode -eq 200) { $httpOk = $true; break }
    } catch { }
}

# ── آمادگی: ربات باید "Application started" و سپس getUpdates بزند ─────────────
$botStarted = $false
$botPolling = $false
$botRestarts = 0
# ربات وقتی به api.telegram.org نرسد با پیامِ روشن و کد ۳ خارج می‌شود؛
# بالا آوردنِ دوباره در حلقه فایده‌ای ندارد و فقط لاگ را شلوغ می‌کند.
$botOffline = $false
if ($botProc) {
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Milliseconds 500
        if ($botProc.HasExited) {
            $early = Read-Log @($botOut, $botErr)
            if ($early -match 'telegram API unreachable') {
                $botOffline = $true; break
            }
            # شبکه می‌تواند هنگام getMe تایم‌اوت بدهد؛ یک بار دیگر بالا بیاور
            # تا گزارشِ اولیه دروغ نگوید که ربات بالا نیامده.
            if ($NoRestart -or $botRestarts -ge 1) { break }
            $botRestarts++
            Write-Host ("[watch] bot exited during startup -> restarting once" ) -ForegroundColor Yellow
            Start-Sleep -Seconds 3
            $botProc = Start-Bot
            continue
        }
        $txt = Read-Log @($botOut, $botErr)
        if ($txt -and $txt -match 'Application started') {
            $botStarted = $true
            if ($txt -match 'getUpdates') { $botPolling = $true; break }
        }
    }
    if (-not $botPolling -and -not $botProc.HasExited) {
        Start-Sleep -Seconds 10
        $txt = Read-Log @($botOut, $botErr)
        if ($txt -match 'getUpdates') { $botPolling = $true }
    }
}

# ── گزارش وضعیت اولیه ────────────────────────────────────────────────────────
Write-Host ""
Write-Host "================ Free-v2ray-Configs : local services ================" -ForegroundColor Cyan
if ($httpOk) {
    Write-Host ("  [ok]   web     http://127.0.0.1:{0}/docs/" -f $Port) -ForegroundColor Green
    Write-Host ("                http://127.0.0.1:{0}/docs/fa/" -f $Port)
    Write-Host ("                http://127.0.0.1:{0}/docs/status/" -f $Port)
} else {
    Write-Host "  [fail] web server did not answer $url" -ForegroundColor Red
    Write-Host ("         see {0}" -f $httpErr)
}
Write-Host ("         pid {0}" -f $httpProc.Id)

if ($botProc) {
    if ($botStarted -and $botPolling) {
        Write-Host ("  [ok]   bot     polling (getUpdates)" ) -ForegroundColor Green
    } elseif ($botStarted) {
        Write-Host "  [warn] bot     started but no getUpdates yet (check proxy/network)" -ForegroundColor Yellow
    } else {
        $botLogText = Read-Log @($botOut, $botErr)
        if ($botOffline -or $botLogText -match 'telegram API unreachable|telegram\.error\.(TimedOut|NetworkError)|httpx\.') {
            Write-Host "  [warn] bot     telegram API unreachable (network/proxy) - web is up; restart after fixing network" -ForegroundColor Yellow
        } else {
            Write-Host "  [fail] bot     did not start" -ForegroundColor Red
        }
        Write-Host ("         see {0} / {1}" -f $botOut, $botErr)
    }
    Write-Host ("         pid {0}   log: {1}" -f $botProc.Id, $botErr)
} else {
    Write-Host "  [skip] bot" -ForegroundColor DarkGray
}

Write-Host ("  logs: {0}" -f $logDir)
Write-Host "  Ctrl+C stops everything."
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

if (-not $httpOk -and $httpProc.HasExited) {
    Write-Host "web server exited; tail of its error log:" -ForegroundColor Red
    Get-Content -Tail 15 -ErrorAction SilentlyContinue $httpErr | ForEach-Object { Write-Host "  $_" }
    if ($botProc -and -not $botProc.HasExited) { Stop-Process -Id $botProc.Id -Force -ErrorAction SilentlyContinue }
    exit 1
}

# ── نگه‌داشتنِ سرویس‌ها تا Ctrl+C (با ری‌استارتِ خودکار) ───────────────────────
function Stop-Children {
    foreach ($p in @($httpProc, $botProc)) {
        if ($p -and -not $p.HasExited) {
            try { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue } catch { }
        }
    }
}

try {
    while ($true) {
        Start-Sleep -Seconds 2

        if ($httpProc.HasExited) {
            Write-Host ("[watch] web server exited (code {0})" -f $httpProc.ExitCode) -ForegroundColor Yellow
            Get-Content -Tail 8 -ErrorAction SilentlyContinue $httpErr | ForEach-Object { Write-Host "  $_" }
            if ($NoRestart) { break }
            Start-Sleep -Seconds 3
            $httpProc = Start-HttpServer
            Write-Host ("[watch] web server restarted, pid {0}" -f $httpProc.Id) -ForegroundColor Yellow
        }

        if ($botProc -and $botProc.HasExited) {
            if ($botOffline) {
                # قبلاً یک بار با پیامِ روشن گزارش شد؛ تلاشِ دوباره بی‌فایده است.
                $botProc = $null
                continue
            }
            Write-Host ("[watch] bot exited (code {0})" -f $botProc.ExitCode) -ForegroundColor Yellow
            Get-Content -Tail 8 -ErrorAction SilentlyContinue $botOut | ForEach-Object { Write-Host "  $_" }
            Get-Content -Tail 8 -ErrorAction SilentlyContinue $botErr | ForEach-Object { Write-Host "  $_" }
            if ($NoRestart) { break }
            Start-Sleep -Seconds 5
            $botProc = Start-Bot
            Write-Host ("[watch] bot restarted, pid {0}" -f $botProc.Id) -ForegroundColor Yellow
        }
    }
} finally {
    Write-Host ""
    Write-Host "stopping services..." -ForegroundColor Cyan
    Stop-Children
    Write-Host "stopped." -ForegroundColor Cyan
}
