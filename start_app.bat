@echo off
title Smart Strap Server

REM Change to the folder where this .bat lives
cd /d "%~dp0"

REM Open browser after 3 seconds in background
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:5000"

REM Run Flask in a window that NEVER auto-closes (cmd /k keeps it open)
cmd /k "echo. & echo Starting Smart Strap Server... & echo Keep this window open while using the app. & echo. & py server.py & echo. & echo SERVER STOPPED. You can close this window."
