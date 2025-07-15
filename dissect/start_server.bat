@echo off
echo PDF Extractor Local Server
echo ========================

REM Check if local_server.py exists
if not exist "local_server.py" (
    echo Error: local_server.py not found in current directory
    echo Please run this from the PDF extraction output directory
    pause
    exit /b 1
)

echo Attempting to start local server...
echo.

REM Try Python 3 first
python local_server.py
if %errorlevel% neq 0 (
    echo.
    echo Python server failed. Trying alternative method...
    echo.
    
    REM Try Python built-in server as fallback
    echo Starting Python built-in server on port 8080...
    python -m http.server 8080
    if %errorlevel% neq 0 (
        echo.
        echo All server methods failed. You can:
        echo 1. Run as administrator
        echo 2. Check Windows Firewall settings
        echo 3. Open the HTML file directly in your browser
        echo    ^(AI analysis will work with canvas fallback^)
        echo.
        pause
    )
)

pause
