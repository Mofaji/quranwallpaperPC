@echo off
taskkill /F /IM "node.exe" /FI "WINDOWTITLE eq wallpaper-setter*" 2>nul
timeout /t 2 /nobreak >nul
start /b "" wscript.exe launch.vbs
exit