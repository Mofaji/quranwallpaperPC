const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Create logs directory if it doesn't exist
const logsDir = path.join(__dirname, 'logs');
if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir);
}

// Create log file
const logFile = fs.createWriteStream(
    path.join(logsDir, `wallpaper-${new Date().toISOString().split('T')[0]}.log`),
    { flags: 'a' }
);

console.log('Starting wallpaper service...');
logFile.write(`\n[${new Date().toISOString()}] Starting wallpaper service...\n`);

const wallpaperProcess = spawn('node', ['wallpaper-setter.js'], {
    stdio: ['pipe', 'pipe', 'pipe']
});

wallpaperProcess.stdout.on('data', (data) => {
    const message = `[${new Date().toISOString()}] ${data}`;
    console.log(message);
    logFile.write(message);
});

wallpaperProcess.stderr.on('data', (data) => {
    const message = `[${new Date().toISOString()}] ERROR: ${data}`;
    console.error(message);
    logFile.write(message);
});

wallpaperProcess.on('close', (code) => {
    const message = `[${new Date().toISOString()}] Process exited with code ${code}\n`;
    console.log(message);
    logFile.write(message);
});