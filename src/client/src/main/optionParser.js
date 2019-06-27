const fs = require('fs')
const {dialog} = require('electron')
const homedir = require('os').homedir()
const settingsDirPath = homedir + '/.TeamCode-settings/'
const settingsPath = settingsDirPath + 'settings.json'
const defaultSettings = { serverURL: 'ws://segfault.party:12345', workingPath: '' }

/**
 * This function writes the given settings object to a JSON file.
 *
 * @param {Object} settings settings object
 */
function writeJSON (settings) {
  /* Make the TeamCode-settings directory if it does not exist yet. */
  if (!fs.existsSync(settingsDirPath)) fs.mkdirSync(settingsDirPath)

  /* Stringify the settings opject and write it to the settings.json file. */
  let jsonSettingsString = JSON.stringify(settings)

  /* Check if settings object is correct. */
  if (!correctJSON(settings)) {
    jsonSettingsString = JSON.stringify(defaultSettings)
  }

  fs.writeFileSync(settingsPath, jsonSettingsString, 'utf8')
}

/**
 * This function checks if the given object has the right member-types.
 *
 * @param {Object} currSettings settings object
 */
function correctJSON (currSettings) {
  /* The serverURL and workingpath need to be strings. */
  return typeof currSettings.serverURL === 'string' && typeof currSettings.workingPath === 'string'
}

/**
 * Sets a new serverURL or new local workspace.
 *
 * @param {string} newString either new working path or new serverURL
 * @param {Object} settings default settings object, used when json file does
 *                          not exist yet.
 * @param {string} member either 'server' or 'workspace', indicating which
 *                        member to set.
 */
function setter (newString, settings, member) {
  /* Check if newString is a string. */
  if (typeof newString !== 'string') return

  /* If json file does not exist, create a new one with the given settings. */
  if (!fs.existsSync(settingsPath)) {
    writeJSON(settings)
    return
  }

  /* If settings json file exists, read the file and update the given member.
   * Write the new object to the json file.
   */
  let jsonSettingsString = fs.readFileSync(settingsPath, 'utf8')
  let currSettings = {}

  try {
    currSettings = JSON.parse(jsonSettingsString)
  } catch (err) {
    dialog.showErrorBox('JSON parse error', err)
    writeJSON(defaultSettings)
    return
  }

  switch (member) {
    case 'server':
      currSettings.serverURL = newString
      writeJSON(currSettings)
      break
    case 'workspace':
      currSettings.workingPath = newString
      writeJSON(currSettings)
      break
    default:
      writeJSON(defaultSettings)
  }
}

/**
 * Read the settings object from the JSON file if it exists.
 * Otherwise return the predefined settings object.
 */
export function getSettings () {
  /* Make a JSON file if it does not exist yet, otherwise read the JSON file. */
  if (!fs.existsSync(settingsPath)) {
    writeJSON(defaultSettings)
    return defaultSettings
  }

  let jsonSettingsString = fs.readFileSync(settingsPath, 'utf8')
  try {
    let currSettings = JSON.parse(jsonSettingsString)

    /* If this settings object is not correct,
     * write the default settings to the json file and return that.
     */
    if (!correctJSON(currSettings)) {
      writeJSON(defaultSettings)
      return defaultSettings
    }

    return currSettings
  } catch (err) {
    dialog.showErrorBox('JSON parse error', err)
    writeJSON(defaultSettings)
    return defaultSettings
  }
}

/**
 * This function changes the serverURL in the settings.json file.
 *
 * @param {string} newServerURL new server URL
 */
export function setServerURL (newServerURL) {
  let currSettings = {serverURL: newServerURL, workingPath: ''}
  setter(newServerURL, currSettings, 'server')
}

/**
 * This function sets the localWorkingPath in the settings.json file.
 *
 * @param {string} localWorkingPath path to local directory
 */
export function setLocalWorkspace (localWorkingPath) {
  let currSettings = {serverURL: defaultSettings.serverURL, workingPath: localWorkingPath}
  setter(localWorkingPath, currSettings, 'workspace')
}

/**
 * This function resets the serverURL in the json file.
 */
export function resetServerURL () {
  setServerURL(defaultSettings.serverURL)
}
