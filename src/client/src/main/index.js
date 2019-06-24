'use strict'

import { app, BrowserWindow, Menu } from 'electron'
const prompt = require('electron-prompt')

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
    webPreferences: {
      nodeIntegration: true // attempt to fix process not found error
    }
  })

  mainWindow.setFullScreenable(true)

  mainWindow.loadURL(winURL)

  const homedir = require('os').homedir()
  const settingsDirPath = homedir + '/pseditor-settings/'
  const settingsPath = settingsDirPath + 'settings.json'
  const dialog = require('electron').dialog
  const fs = require('fs')
  const menu = Menu.buildFromTemplate([
    {
      label: 'Settings',
      submenu: [
        {
          label: 'Server Connection',
          click () {
            prompt({
              title: 'New Server URL',
              label: 'URL',
              value: 'ws://segfault.party:12345'
            }).then((newURLString) => {
              if (newURLString !== undefined && newURLString !== null) {
                mainWindow.webContents.send('changeURL', newURLString)
              }
            })
          }
        },
        {
          label: 'Local Workspace',
          click () {
            let settings = {serverURL: '', workingPath: ''}

            /* Let user select local directory. */
            let localDirPath = dialog.showOpenDialog({ properties: ['openDirectory'] })

            if (localDirPath === undefined || localDirPath[0].toString() === '') {
              return
            } else {
              settings.workingPath = localDirPath[0].toString()
            }

            /* If settings json file exists, read the server member from the JSON object. */
            if (fs.existsSync(settingsPath)) {
              let jsonSettingsString = fs.readFileSync(settingsPath, 'utf8')
              try {
                settings.serverURL = JSON.parse(jsonSettingsString).serverURL
              } catch (err) {
                console.error(err)
              }
            }

            /* Make a json object and write it to the settings.json file. */
            const jsonSettingsString = JSON.stringify(settings)

            /* Make the pseditor-settings directory if it does not exist yet. */
            if (!fs.existsSync(settingsDirPath)) fs.mkdirSync(settingsDirPath)

            /* Write json string to file. */
            fs.writeFile(settingsPath, jsonSettingsString, 'utf8', (e) => {
              if (e) console.error(e)
            })
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
