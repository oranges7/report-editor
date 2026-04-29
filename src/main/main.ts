import { app, BrowserWindow, ipcMain, dialog } from 'electron'
import * as fs from 'fs'
import * as path from 'path'

let mainWindow: BrowserWindow | null = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 900,
    minHeight: 600,
    frame: false,
    titleBarStyle: 'hidden',
    titleBarOverlay: {
      color: '#0d0f14',
      symbolColor: '#9aa0b0',
      height: 40
    },
    backgroundColor: '#0d0f14',
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show()
  })

  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

ipcMain.handle('dialog:openFile', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters: [{ name: 'Text Files', extensions: ['txt'] }, { name: 'All Files', extensions: ['*'] }]
  })
  if (!result.canceled && result.filePaths.length > 0) {
    const filePath = result.filePaths[0]
    const content = fs.readFileSync(filePath, 'utf-8')
    return { filePath, content }
  }
  return null
})

ipcMain.handle('dialog:selectFile', async (_event, fileType: string) => {
  let filters: { name: string; extensions: string[] }[]

  switch (fileType) {
    case 'image':
      filters = [
        { name: 'Image Files', extensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp'] },
        { name: 'All Files', extensions: ['*'] }
      ]
      break
    case 'table':
      filters = [
        { name: 'Table Files', extensions: ['xlsx', 'xls', 'csv', 'tsv', 'txt'] },
        { name: 'All Files', extensions: ['*'] }
      ]
      break
    default:
      filters = [{ name: 'All Files', extensions: ['*'] }]
  }

  const result = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters
  })
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0]
  }
  return null
})

ipcMain.handle('dialog:saveFile', async (_event, content: string) => {
  const result = await dialog.showSaveDialog({
    filters: [{ name: 'Text Files', extensions: ['txt'] }, { name: 'All Files', extensions: ['*'] }]
  })
  if (!result.canceled && result.filePath) {
    fs.writeFileSync(result.filePath, content, 'utf-8')
    return result.filePath
  }
  return null
})

ipcMain.handle('file:readFile', async (_event, filePath: string) => {
  try {
    const content = fs.readFileSync(filePath, 'utf-8')
    return content
  } catch {
    return null
  }
})

ipcMain.handle('file:writeFile', async (_event, filePath: string, content: string) => {
  try {
    fs.writeFileSync(filePath, content, 'utf-8')
    return true
  } catch {
    return false
  }
})

ipcMain.handle('dialog:openDirectory', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openDirectory']
  })
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0]
  }
  return null
})

ipcMain.handle('fs:readdir', async (_event, dirPath: string) => {
  try {
    const files = fs.readdirSync(dirPath, { withFileTypes: true })
    return files.map(file => ({
      name: file.name,
      isDirectory: file.isDirectory(),
      path: path.join(dirPath, file.name)
    }))
  } catch {
    return []
  }
})

ipcMain.handle('path:relative', async (_event, from: string, to: string) => {
  return path.relative(from, to).replace(/\\/g, '/')
})

ipcMain.handle('path:join', async (_event, ...paths: string[]) => {
  return path.join(...paths)
})

ipcMain.handle('window:setTitleBarTheme', async (_event, theme: 'light' | 'dark') => {
  if (mainWindow) {
    const bgColor = theme === 'light' ? '#eff1f5' : '#0d0f14'
    const symbolColor = theme === 'light' ? '#5c5f77' : '#9aa0b0'
    mainWindow.setTitleBarOverlay({
      color: bgColor,
      symbolColor
    })
  }
})
