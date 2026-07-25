@echo off
title Smart Strap Server

REM Change to the folder where this .bat lives
cd /d "%~dp0"

REM Try to start MySQL80 (requires admin rights — safe to ignore if already running)
net start MySQL80 >nul 2>&1

REM Open browser after 3 seconds in background
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:5000"

REM Run Flask — uses full py.exe path so it works regardless of PATH settings
cmd /k "echo. & echo Starting Smart Strap Server... & echo Keep this window open while using the app. & echo. & C:\Windows\py.exe server.py & echo. & echo SERVER STOPPED. You can close this window."
