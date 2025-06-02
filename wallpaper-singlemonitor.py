import os
import asyncio
import aiohttp
import random
import time
import sys
import ctypes
from pathlib import Path
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

WALLPAPER_DIR = Path(__file__).parent / 'wallpapers'
OUTPUT = WALLPAPER_DIR / 'wallpaper_single.png'
TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080

async def get_random_background():
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
    try:
        async with aiohttp.ClientSession() as session:
            surah = random.randint(1, 114)
            surah_url = f"https://api.alquran.cloud/v1/surah/{surah}"
            async with session.get(surah_url) as response:
                data = await response.json()
            if not data.get('data') or not data['data'].get('ayahs') or len(data['data']['ayahs']) == 0:
                raise Exception('Invalid API response')
            random_ayah_index = random.randint(0, len(data['data']['ayahs']) - 1)
            ayah = data['data']['ayahs'][random_ayah_index]
            translation_url = f"https://api.alquran.cloud/v1/ayah/{ayah['number']}/en.sahih"
            transliteration_url = f"https://api.alquran.cloud/v1/ayah/{ayah['number']}/en.transliteration"
            async with session.get(translation_url) as trans_response:
                translation_data = await trans_response.json()
            async with session.get(transliteration_url) as translit_response:
                transliteration_data = await translit_response.json()
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

async def generate_wallpaper(verse, background):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'--window-size={TARGET_WIDTH},{TARGET_HEIGHT}')
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    margin: 0;
                    height: 100vh;
                    width: 100vw;
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
        temp_html = WALLPAPER_DIR / 'temp_single.html'
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        driver.get(f'file://{temp_html.absolute()}')
        time.sleep(2)
        image_path = WALLPAPER_DIR / 'wallpaper_single.png'
        driver.save_screenshot(str(image_path))
        temp_html.unlink()
        print(f'[DEBUG] Wallpaper generated: {image_path}')
        return str(image_path)
    finally:
        if driver:
            driver.quit()

async def set_wallpaper(image_path):
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "6")  # 6 = Stretch
        winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(key)
    except Exception as e:
        print(f"[WARNING] Failed to set wallpaper style: {e}")
    result = ctypes.windll.user32.SystemParametersInfoW(20, 0, str(image_path), 3)
    if result:
        print("[SUCCESS] Wallpaper set successfully.")
    else:
        print("[ERROR] Failed to set wallpaper.")

async def main():
    WALLPAPER_DIR.mkdir(exist_ok=True)
    background = await get_random_background()
    ayat = await get_random_ayat()
    image_path = await generate_wallpaper(ayat, background)
    await set_wallpaper(image_path)
    await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
