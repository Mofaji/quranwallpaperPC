import os
import asyncio
import aiohttp
import random
import time
import subprocess
import sys
import ctypes
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Constants
WALLPAPER_DIR = Path(__file__).parent / 'wallpapers'
OUTPUT = WALLPAPER_DIR / 'combined_wallpaper.png'
TARGET_HEIGHT = 1080
UPDATE_INTERVAL = 30 * 60  # 30 minutes in seconds

async def get_random_background():
    """Fetch a random background image from Unsplash API."""
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.unsplash.com/photos/random?query=nature,landscape,mountains&client_id=oZQma7v_znVRCBBdlJt5jwPwuyt2O4DfYHL350hq_rA"
            async with session.get(url) as response:
                data = await response.json()
                return data['urls']['regular']
    except Exception as error:
        print(f'Error fetching background: {error}')
        return 'https://images.unsplash.com/photo-1506744038136-46273834b3fb'

async def get_random_ayat():
    """Fetch a random Quranic verse with translation and transliteration."""
    try:
        async with aiohttp.ClientSession() as session:
            # Get random surah
            surah = random.randint(1, 114)
            
            # Fetch surah data
            surah_url = f"https://api.alquran.cloud/v1/surah/{surah}"
            async with session.get(surah_url) as response:
                data = await response.json()
                
            if not data.get('data') or not data['data'].get('ayahs') or len(data['data']['ayahs']) == 0:
                raise Exception('Invalid API response')
            
            # Get random ayah from the surah
            random_ayah_index = random.randint(0, len(data['data']['ayahs']) - 1)
            ayah = data['data']['ayahs'][random_ayah_index]
            
            # Fetch translation and transliteration
            translation_url = f"https://api.alquran.cloud/v1/ayah/{ayah['number']}/en.sahih"
            transliteration_url = f"https://api.alquran.cloud/v1/ayah/{ayah['number']}/en.transliteration"
            
            async with session.get(translation_url) as trans_response:
                translation_data = await trans_response.json()
            
            async with session.get(transliteration_url) as translit_response:
                transliteration_data = await translit_response.json()
            
            # Remove Bismillah variants from Arabic text
            arabic_text = ayah['text']
            bismillah_variants = [
                'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ',
                'بِّسۡمِ ٱللَّهِ ٱلرَّحۡمَـٰنِ ٱلرَّحِیمِ',
                'بِسْمِ اللَّٰهِ الرَّحْمَٰنِ الرَّحِيمِ',
                'بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ',
                'بِسۡمِ ٱللَّهِ ٱلرَّحۡمَـٰنِ ٱلرَّحِیمِ'
            ]
            
            for variant in bismillah_variants:
                arabic_text = arabic_text.replace(variant, '').strip()
            
            return {
                'arabic': arabic_text,
                'english': translation_data['data']['text'],
                'transcription': transliteration_data['data']['text'],
                'surah': surah,
                'ayah': ayah['numberInSurah']
            }
            
    except Exception as error:
        print(f'Error fetching ayat: {error}')
        return {
            'arabic': 'Error loading verse',
            'english': 'Please try again',
            'transcription': 'Error loading verse',
            'surah': '',
            'ayah': ''
        }

async def generate_wallpaper(verse, background, index):
    """Generate a wallpaper using Selenium WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        html_content = f"""
        <html>
        <head>
            <style>                body {{
                    margin: 0;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('{background}');
                    background-size: 100% 100%;
                    color: white;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 2rem;
                    overflow: hidden;
                }}
                .arabic {{ font-size: 3rem; margin-bottom: 1rem; }}
                .transcription {{ font-size: 1.8rem; margin-bottom: 1rem; font-style: italic; }}
                .english {{ font-size: 1.5rem; margin-bottom: 1rem; }}
                .reference {{ font-size: 1rem; }}
            </style>
        </head>
        <body>
            <div class="arabic">{verse['arabic']}</div>
            <div class="transcription">{verse['transcription']}</div>
            <div class="english">{verse['english']}</div>
            <div class="reference">Surah {verse['surah']}:{verse['ayah']}</div>
        </body>
        </html>
        """
        
        # Create a temporary HTML file
        temp_html = WALLPAPER_DIR / f'temp_{index}.html'
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Load the HTML file
        driver.get(f'file://{temp_html.absolute()}')
        
        # Wait for the page to load
        time.sleep(2)
        
        # Take screenshot
        image_path = WALLPAPER_DIR / f'wallpaper_{index}.png'
        driver.save_screenshot(str(image_path))
        
        # Clean up temp file
        temp_html.unlink()
        
        print(f'[DEBUG] Wallpaper generated: {image_path}')
        return str(image_path)
        
    finally:
        if driver:
            driver.quit()

async def combine_wallpapers():
    """Combine three wallpapers for multi-monitor setup."""
    images = [
        WALLPAPER_DIR / 'wallpaper_0.png',
        WALLPAPER_DIR / 'wallpaper_1.png',
        WALLPAPER_DIR / 'wallpaper_2.png',
    ]
    
    try:
        # Open and resize images for different monitors
        img0 = Image.open(images[0]).resize((1306, 968))  # Monitor 1 (1366x768 @ 125%)
        img1 = Image.open(images[1]).resize((1782, 964))  # Monitor 2 (1920x1080 @ 125%)
        img2 = Image.open(images[2]).resize((1820, 1080))  # Monitor 3 (already scaled 1536x864)

        # Calculate total dimensions
        total_width = img0.width + img1.width + img2.width
        max_height = max(img0.height, img1.height, img2.height, TARGET_HEIGHT)
        
        # Create combined image
        combined = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 255))
        
        # Paste images side by side
        combined.paste(img0, (0, 0))
        combined.paste(img1, (img0.width, 0))
        combined.paste(img2, (img0.width + img1.width, 0))
        
        # Save combined wallpaper
        combined.save(OUTPUT, 'PNG')
        print(f'[DEBUG] Combined wallpaper created: {OUTPUT}')
        
    except Exception as error:
        print(f'[ERROR] Failed to combine wallpapers: {error}')
        sys.exit(1)

async def set_wallpaper(image_path):
    """Sets the wallpaper using Windows API with Stretch style."""
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "22")  # 5 = Fill
        winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"[WARNING] Failed to set wallpaper style: {e}")

    # Set the wallpaper
    result = ctypes.windll.user32.SystemParametersInfoW(20, 0, str(image_path), 3)
    if result:
        print("[SUCCESS] Wallpaper set successfully with Stretch style.")
    else:
        print("[ERROR] Failed to set wallpaper.")

async def main():
    """Main function to generate and set wallpapers."""
    # Create wallpaper directory
    WALLPAPER_DIR.mkdir(exist_ok=True)
    
    # Generate wallpapers for each monitor
    for i in range(3):
        background = await get_random_background()
        ayat = await get_random_ayat()
        await generate_wallpaper(ayat, background, i)
    
    # Combine wallpapers
    await combine_wallpapers()
    
    # Set wallpaper
    await set_wallpaper(OUTPUT)
    
    # Wait 10 seconds to ensure all processes complete
    await asyncio.sleep(5)


if __name__ == "__main__":
    # Run once immediately, then continuously
    asyncio.run(main())
    