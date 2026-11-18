@echo off
title Smart Strap Server

REM Change to the folder where this .bat lives
cd /d "%~dp0"

REM Optional page to open, e.g.  start_app.bat admin   (default: patient/doctor login)
set "APP_URL=http://localhost:5000/"
if /i "%~1"=="admin" set "APP_URL=http://localhost:5000/admin"

REM Try to start MySQL80 (requires admin rights — safe to ignore if already running)
net start MySQL80 >nul 2>&1

REM If the server is already running, just open the browser and exit
netstat -ano | findstr ":5000 " | findstr LISTENING >nul
if %errorlevel%==0 (
    start "" "%APP_URL%"
    exit /b
)

REM Open browser after 3 seconds in background
start "" cmd /c "timeout /t 3 /nobreak >nul & start %APP_URL%"

REM Run Flask — uses full py.exe path so it works regardless of PATH settings
cmd /k "echo. & echo Starting Smart Strap Server... & echo Keep this window open while using the app. & echo. & C:\Windows\py.exe server.py & echo. & echo SERVER STOPPED. You can close this window."
