@echo off
rem starts every local service (web server + telegram bot) and keeps them running.
rem Ctrl+C stops all of them. Options: -Port 8124  -NoBot  -NoRestart
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run_local.ps1" %*
set "rc=%ERRORLEVEL%"
if not "%rc%"=="0" pause
exit /b %rc%
