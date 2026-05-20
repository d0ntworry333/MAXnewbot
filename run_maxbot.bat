@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ===== MAX Fitness Bot =====
echo.

if not exist ".env" (
    echo [ERROR] File .env not found. Copy .env.example to .env and set MAX_BOT_TOKEN.
    pause
    exit /b 1
)

set "LAUNCHER="
where py >nul 2>&1
if not errorlevel 1 (
    set "LAUNCHER=py"
) else (
    where python >nul 2>&1
    if not errorlevel 1 set "LAUNCHER=python"
)
if not defined LAUNCHER (
    echo [ERROR] Neither "py" nor "python" was found. Install Python and add it to PATH.
    pause
    exit /b 1
)

set "EXIST_PID="
for /f "delims=" %%I in ('powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\check_duplicate.ps1" -ProjectRoot "%CD%" 2^>nul') do set "EXIST_PID=%%I"

if defined EXIST_PID (
    echo [ALREADY RUNNING] Bot from this folder is already running. PID: !EXIST_PID!
    echo Close that window or end the task in Task Manager.
    pause
    exit /b 2
)

echo Starting bot... Close this window or press Ctrl+C to stop.
echo.

%LAUNCHER% app\main.py
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
    echo.
    echo ========================================
    echo [ERROR] Exit code: %EXITCODE%
    echo Read the Python traceback ABOVE in this window.
    echo ========================================
    echo.
)

pause
exit /b %EXITCODE%
