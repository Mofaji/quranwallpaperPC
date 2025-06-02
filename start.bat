@echo off
cd /d "%~dp0"
echo [INFO] Starting Quran Wallpaper Generator...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed! Please install Python 3.7 or higher.
    exit /b 1
)

REM Check if required packages are installed
echo [CHECK] Verifying required packages...
python -c "import PIL, selenium, aiohttp" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installing required packages...
    pip install pillow selenium aiohttp
)

REM Create wallpapers directory if it doesn't exist
if not exist "wallpapers" mkdir wallpapers

echo [START] Running wallpaper generator...
python wallpaper-singlemonitor.py

if errorlevel 1 (
    echo [ERROR] The script encountered an error!
    exit /b 1
)

REM No pause, auto close