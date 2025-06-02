@echo off
echo Installing Quran Wallpaper...
npm install --silent puppeteer wallpaper
mkdir "%APPDATA%\QuranWallpaper" 2>nul
xcopy /E /I /Y "%~dp0*" "%APPDATA%\QuranWallpaper" >nul
schtasks /create /tn "QuranWallpaper" /tr "wscript.exe \"%APPDATA%\QuranWallpaper\launch.vbs\"" /sc onlogon /rl highest
echo Installation complete! The wallpaper will start automatically when you log in.
start /b "" wscript.exe "%APPDATA%\QuranWallpaper\launch.vbs"
exit