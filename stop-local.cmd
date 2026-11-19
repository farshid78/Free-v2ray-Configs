@echo off
rem Stop only THIS project's local instances (web on 8123 + Telegram bot).
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\stop_local.ps1"
if errorlevel 1 pause
