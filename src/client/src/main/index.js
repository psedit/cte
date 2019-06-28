'use strict'

import { app, BrowserWindow, Menu } from 'electron'
import * as optionParser from './optionParser'

const prompt = require('electron-prompt')
const dialog = require('electron').dialog
const path = require('path')

/**
 * Set `__static` path to static files in production
 * https://simulatedgreg.gitbooks.io/electron-vue/content/en/using-static-assets.html
 */
if (process.env.NODE_ENV !== 'development') {
  global.__static = require('path').join(__dirname, '/static').replace(/\\/g, '\\\\')
}

let mainWindow
const winURL = process.env.NODE_ENV === 'development'
  ? `http://localhost:9080`
  : `file://${__dirname}/index.html`

function createWindow () {
  /**
   * Initial window options
   */
  mainWindow = new BrowserWindow({
    height: 563,
    useContentSize: true,
    width: 1000,
    icon: path.join(__dirname, '../../build/icons/256x256.png'),
    webPreferences: {
      nodeIntegration: true // attempt to fix process not found error
    }
  })

  mainWindow.setFullScreenable(true)

  mainWindow.loadURL(winURL)

  const menu = Menu.buildFromTemplate([
    {
      label: 'Settings',
      submenu: [
        {
          label: 'Server Connection',
          click () {
            /* Try to read URL from settings file
             */
            let currSettings = optionParser.getSettings()
            /* Ask user for URL.
             */
            prompt({
              title: 'New Server URL',
              label: 'URL',
              value: currSettings.serverURL
            }).then((newURLString) => {
              if (newURLString !== undefined && newURLString !== null) {
                let toast = `Switching to server ${newURLString}`
                mainWindow.webContents.send('changeURL', {url: newURLString, toast: toast})
              }
            })
          }
        },
        {
          label: 'Local Workspace',
          click () {
            /* Let user select local directory. */
            let localDirPath = dialog.showOpenDialog({ properties: ['openDirectory'] })

            if (localDirPath === undefined || localDirPath[0].toString() === '') {
              return
            }

            optionParser.setLocalWorkspace(localDirPath[0].toString())

            /* Send a toast. */
            let toast = `Succesfully set ${localDirPath[0].toString()} as local workspace`
            mainWindow.webContents.send('showWorkspaceToast', toast)
          }
        }
      ]
    }
  ])
  Menu.setApplicationMenu(menu)

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.on('ready', createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})

/**
 * Auto Updater
 *
 * Uncomment the following code below and install `electron-updater` to
 * support auto updating. Code Signing with a valid certificate is required.
 * https://simulatedgreg.gitbooks.io/electron-vue/content/en/using-electron-builder.html#auto-updating
 */

/*
import { autoUpdater } from 'electron-updater'

autoUpdater.on('update-downloaded', () => {
  autoUpdater.quitAndInstall()
})

app.on('ready', () => {
  if (process.env.NODE_ENV === 'production') autoUpdater.checkForUpdates()
})
 */
