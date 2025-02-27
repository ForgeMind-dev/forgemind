import { app, BrowserWindow } from 'electron';
import * as path from 'path';

const isDev = !app.isPackaged;

async function createWindow(): Promise<void> {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      // preload: path.join(__dirname, 'preload.js'),
    },
  });
  if (isDev) {
    await win.loadURL('http://localhost:3000/#/dashboard');
  } else {
    const staticPath = path.join(process.resourcesPath, 'webapp-build', 'index.html');
    // Use loadURL with a file protocol and append the hash for the dashboard route.
    await win.loadURL(`file://${staticPath}#/dashboard`);
  }  
}

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
