// src/main/main.ts

import { app, BrowserWindow } from 'electron';
import * as path from 'path';

// Helper to check if we're in dev mode
const isDev = !app.isPackaged;

let mainWindow: BrowserWindow | null = null;

// Ensure a single instance of the app
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  // If we couldn't get the lock, it means another instance is already running
  app.quit();
} else {
  // Handle deep links when a second instance is launched
  app.on('second-instance', (event, argv) => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
    // Look for a deep link in the arguments (Windows passes it here)
    const deepLinkUrl = argv.find(arg => arg.startsWith('forgemind://'));
    if (deepLinkUrl && mainWindow) {
      console.log('Received deep link in second-instance:', deepLinkUrl);
      // Wait until the current page finishes loading then send the navigation message.
      mainWindow.webContents.once('did-finish-load', () => {
        mainWindow?.webContents.send('navigate-to', '/dashboard');
      });
    }
  });

  // Register the custom protocol
  if (!app.isPackaged) {
    // In dev mode, use process.execPath workaround
    app.setAsDefaultProtocolClient(
      'forgemind',
      process.execPath,
      [path.resolve(process.argv[1])]
    );
  } else {
    // In production, just register the protocol.
    app.setAsDefaultProtocolClient('forgemind');
  }

  // Create the main window when ready
  app.whenReady().then(() => {
    createWindow();

    // If the app was launched with a deep link, wait until loading is done then send the navigation command.
    const deepLinkUrl = process.argv.find(arg => arg.startsWith('forgemind://'));
    if (deepLinkUrl && mainWindow) {
      console.log('Launched with deep link:', deepLinkUrl);
      mainWindow.webContents.once('did-finish-load', () => {
        mainWindow?.webContents.send('navigate-to', '/dashboard');
      });
    }

    app.on('activate', () => {
      // On macOS, re-create a window when the dock icon is clicked and no windows are open.
      if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
  });

  // Handle macOS deep linking
  app.on('open-url', (event, url) => {
    event.preventDefault();
    console.log('open-url triggered:', url);
    if (mainWindow) {
      mainWindow.webContents.once('did-finish-load', () => {
        mainWindow?.webContents.send('navigate-to', '/dashboard');
      });
    }
  });

  app.on('window-all-closed', () => {
    // On macOS it is common for applications and their menu bar to stay active until the user quits explicitly.
    if (process.platform !== 'darwin') {
      app.quit();
    }
  });
}

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // In development mode, load the local webapp on port 3000
  if (!app.isPackaged) {
    mainWindow.loadURL('http://localhost:3000');
  } else {
    mainWindow.loadFile(path.join(app.getAppPath(), 'build', 'index.html'));
  }
}
