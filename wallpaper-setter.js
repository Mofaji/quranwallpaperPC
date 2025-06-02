const { setWallpaper } = require('wallpaper');
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// Ensure QuranWallpaper directory exists in AppData
const appDataDir = path.join(process.env.APPDATA, 'QuranWallpaper');
if (!fs.existsSync(appDataDir)) {
    fs.mkdirSync(appDataDir, { recursive: true });
}

async function captureAndSetWallpaper() {
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--headless=new']
        });
        const page = await browser.newPage();
        
        // Set viewport to match desktop resolution
        await page.setViewport({
            width: 1920,
            height: 1080
        });

        // Disable timeout
        page.setDefaultTimeout(0);
        page.setDefaultNavigationTimeout(0);
        
        const htmlPath = path.join(__dirname, 'wallpaper.html');
        await page.goto(`file://${htmlPath}`);
        
        // Wait for content to load
        await page.waitForSelector('#arabic');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        const imagePath = path.join(appDataDir, 'current.png');
        await page.screenshot({ path: imagePath });
        
        // Set wallpaper for all monitors
        await setWallpaper(imagePath, { screen: 'all' });
    } catch (error) {
        // Write error to log file instead of console
        fs.appendFileSync(path.join(appDataDir, 'error.log'), 
            `${new Date().toISOString()}: ${error.message}\n`);
    } finally {
        if (browser) await browser.close();
    }
}

process.on('uncaughtException', (err) => {
    fs.appendFileSync(path.join(appDataDir, 'error.log'), 
        `${new Date().toISOString()} Uncaught Exception: ${err.message}\n`);
});

// Run immediately and then every 30 minutes
captureAndSetWallpaper();
setInterval(captureAndSetWallpaper, 30 * 60 * 1000);