import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  openFile: () => ipcRenderer.invoke('dialog:openFile'),
  selectFile: (fileType: string) => ipcRenderer.invoke('dialog:selectFile', fileType),
  saveFile: (content: string) => ipcRenderer.invoke('dialog:saveFile', content),
  readFile: (filePath: string) => ipcRenderer.invoke('file:readFile', filePath),
  writeFile: (filePath: string, content: string) => ipcRenderer.invoke('file:writeFile', filePath, content),
  openDirectory: () => ipcRenderer.invoke('dialog:openDirectory'),
  readdir: (dirPath: string) => ipcRenderer.invoke('fs:readdir', dirPath),
  relativePath: (from: string, to: string) => ipcRenderer.invoke('path:relative', from, to),
  joinPath: (...paths: string[]) => ipcRenderer.invoke('path:join', ...paths),
  setTitleBarTheme: (theme: 'light' | 'dark') => ipcRenderer.invoke('window:setTitleBarTheme', theme)
})

declare global {
  interface Window {
    electronAPI: {
      openFile: () => Promise<{ filePath: string; content: string } | null>
      selectFile: (fileType: string) => Promise<string | null>
      saveFile: (content: string) => Promise<string | null>
      readFile: (filePath: string) => Promise<string | null>
      writeFile: (filePath: string, content: string) => Promise<boolean>
      openDirectory: () => Promise<string | null>
      readdir: (dirPath: string) => Promise<Array<{ name: string; isDirectory: boolean; path: string }>>
      relativePath: (from: string, to: string) => Promise<string>
      joinPath: (...paths: string[]) => Promise<string>
      setTitleBarTheme: (theme: 'light' | 'dark') => Promise<void>
    }
  }
}
