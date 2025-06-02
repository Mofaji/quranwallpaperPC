# Quran Wallpaper Generator for Multiple Monitors

Automatically generates and sets wallpapers with random Quranic verses on nature backgrounds for multiple monitor setups.

## Features
- Fetches random verses from the Quran with translations and transliterations
- Downloads beautiful nature backgrounds from Unsplash
- Supports multiple monitor setups
- Auto-refreshes wallpapers periodically

## Requirements
- Python 3.7+
- Google Chrome (for Selenium WebDriver)
- Windows OS

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/Mofaji/quranwallpaperPC.git
    cd quranwallpaperPC
    ```

2. Install required packages:
    ```bash
    pip install pillow selenium aiohttp
    ```

3. Create a `wallpapers` directory (will be created automatically on first run)

## Usage

Simply run the start.bat file or use Python directly:

```bash
python wallpaper.py
```

The script will:
1. Generate three wallpapers with random verses
2. Combine them for your multi-monitor setup
3. Set as wallpaper automatically
4. Refresh every 30 minutes

## Files
- `wallpaper.py` - Main script
- `start.bat` - Batch file to run the script
- `wallpapers/` - Directory for generated wallpapers
- `README.md` - This file

## Configuration
Edit `wallpaper.py` to modify:
- Monitor resolutions
- Update interval
- Background image preferences
- Text styling