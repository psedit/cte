const WebSocket = require('ws')
const uuid = require('uuid/v4')
const fs = require('fs')
const {dialog} = require('electron')

// const path = 'ws://bami.party:12345'
const path = 'ws://segfault.party:12345'
const homedir = require('os').homedir()
const settingsDirPath = homedir + '/pseditor-settings/'
const settingsPath = settingsDirPath + 'settings.json'

/**
 * @typedef {Object} Message
 * @property {string} type - The type of message
 * @property {string} uuid - The unique id of the message
 * @property {string} sender - sender service or sender client address
 * @property {string} pref_dest - sender service or sender client address
 * @property {Object} content - the payload of the message
 *
 * @see https://github.com/psedit/cte/wiki/Server-service-messages
 */

/**
 * @callback connectorCallback
 * @param {Message} The message response.
 */

class Connector {
  /**
   * Collection of all listeners
   *
   * @type {{upgrade: Array, ping: Array, 'unexpected-response': Array, error: Array, pong: Array, message: {all: Array}, close: Array, open: Array}}
   * @private
   */
  listeners = {
    close: [],
    error: [],
    open: [],
    ping: [],
    pong: [],
    'unexpected-response': [],
    upgrade: [],
    message: {
      all: []
    }
  }

  /**
   * The websocket interface.
   *
   * @type {WebSocket}
   */
  ws;

  /**
   *
   * @type {string} URLString
   */
  URLString;

  /**
   * Creates a connection and setups listeners.
   * Also creates a json file or reads path from json file.
   * @param {string} path - The path to the websocket server.
   */
  constructor (path) {
    let settings = {serverURL: path, workingPath: ''}
    /*
     */
    let getFromSettings = () => {
      let jsonSettingsString = fs.readFileSync(settingsPath, 'utf8')
      try {
        let newSettings = JSON.parse(jsonSettingsString)
        if (typeof newSettings.serverURL !== 'string') {
          makeNewSetting()
          return
        } else {
          settings = newSettings
        }
      } catch (err) {
        dialog.showErrorBox('File read error', err)
      }
    }
    let makeNewSetting = () => {
      /* Make a json object and write it to the settings.json file. */
      const jsonSettingsString = JSON.stringify(settings)
      /* Make the pseditor-settings directory if it does not exist yet. */
      if (!fs.existsSync(settingsDirPath)) fs.mkdirSync(settingsDirPath)
      /* Write json string to file. */
      fs.writeFile(settingsPath, jsonSettingsString, 'utf8', (e) => {
        if (e) dialog.showErrorBox(e)
      })
    }
    /* If settings json file exists, read the file and update the settings object. */
    if (fs.existsSync(settingsPath)) {
      getFromSettings()
    } else {
      makeNewSetting()
    }
    this.setUp(settings.serverURL)
  }
  /**
   * Sets up the connector.
   * @param {string} pathString string of URL for websocket.
   */
  setUp (pathString) {
    this.URLString = pathString

    // Setup websocket
    this.ws = new WebSocket(pathString, {
      perMessageDeflate: false
    })
    // Setup listeners
    for (let type in this.listeners) {
      if (type === 'message') {
        this.ws.on('message', (response) => {
          response = JSON.parse(response)

          for (let listener of this.listeners.message.all) {
            listener(response)
          }

          if (response.type in this.listeners.message) {
            for (let listener of this.listeners.message[response.type]) {
              listener(response)
            }
          }
        })
      } else {
        this.ws.on(type, (...args) => {
          for (let listener of this.listeners[type]) {
            listener(...args)
          }
        })
      }
    }
  }
  /**
   * Got form:
   * https://stackoverflow.com/questions/13546424/how-to-wait-for-a-websockets-readystate-to-change
   * @param {function} callback is called when websocket is open
   */
  waitUntillOpen (callback) {
    setTimeout(() => {
      if (this.ws.readyState === 1) {
        if (callback != null) {
          callback()
        }
      } else {
        this.waitUntillOpen(callback)
      }
    }, 5) // wait 5 milisecond for the connection...
  }
  /**
   * Change the server URL and update the JSON file accordingly.
   * @param {string} newPathString string with path for new url
   */
  reload (newPathString) {
    let settings = {serverURL: newPathString, workingPath: ''}

    // TODO: Maak hier een fucntie van (@see constructor)
    /* If settings json file exists, read the file and update the serverURL member. */
    if (fs.existsSync(settingsPath)) {
      let jsonSettingsString = fs.readFileSync(settingsPath, 'utf8')
      try {
        settings = JSON.parse(jsonSettingsString)
        settings.serverURL = newPathString
        fs.writeFile(settingsPath, JSON.stringify(settings), 'utf8', (e) => { if (e) dialog.showErrorBox('File Write Error', e) })
      } catch (err) {
        dialog.showErrorBox('File write error', err)
      }
    } else {
      /* Make a json object and write it to the settings.json file. */
      const jsonSettingsString = JSON.stringify(settings)

      /* Make the pseditor-settings directory if it does not exist yet. */
      if (!fs.existsSync(settingsDirPath)) fs.mkdirSync(settingsDirPath)

      /* Write json string to file. */
      fs.writeFile(settingsPath, jsonSettingsString, 'utf8', (e) => {
        if (e) dialog.showErrorBox('File write error', e)
      })
    }
    this.setUp(settings.serverURL)
  }
  /**
   * Closes connection to websocket server
   *
   * @param {number} code - Status code of why the connection is closing.
   * @param {string} reason - A human readable reason of why the connection is closing.
   */
  close (code = 0, reason = 'I am done.') {
    this.ws.close(code, reason)
  }

  /**
   * Add event listener to the websocket interface.
   *
   * @param {string} type - A websocket event type.
   * @param {connectorCallback} callback - The listener that is called when the specified event happens.
   * @see https://github.com/websockets/ws/blob/HEAD/doc/ws.md#event-close-1
   */
  addEventListener (type, callback) {
    if (!(type in this.listeners)) {
      return
    }

    if (type === 'message') {
      this.listeners.message.all.push(callback)
    } else {
      this.listeners[type].push(callback)
    }
  }

  /**
   * Check if connection is open.
   *
   * @return {Boolean} True if websocket is open, otherwise False.
   */
  isOpen () {
    return this.ws.readyState === WebSocket.OPEN
  }

  /**
   * Removes a listener.
   *
   * @param {string} type - The type of the event.
   * @param {connectorCallback} callback - The function to stop listening to the specific event.
   */
  removeEventListener (type, callback) {
    if (!(type in this.listeners)) {
      return
    }

    let listeners = this.listeners

    if (type === 'message') {
      listeners = listeners.message
    }

    for (const type in listeners) {
      const arr = listeners[type]
      for (let i = 0; i < arr.length; i++) {
        if (arr[i] === callback) {
          arr.splice(i, 1)
          return
        }
      }
    }
  }

  /**
   * Return the String of the URL
   */
  getURLString () {
    return this.URLString
  }
  /**
   * Send some content to the websocket server.
   *
   * @param {string} type - The type of the message.
   * @param {Object} content - The payload of the message.
   * @param {string} [sender = CLIENT] - The identifier of the sender.
   * @param {string} [prefDest = null] - The destination where the message should preferable go.
   */
  send (type, content, sender = 'CLIENT', prefDest = null) {
    const payload = {
      type,
      uuid: uuid(),
      sender,
      pref_def: prefDest,
      content
    }

    this.ws.send(JSON.stringify(payload))
  }

  /**
   * Sends a message and listens for the response.
   * A helper method for messages with a request-response structure.
   *
   * @param {string} requestType - The type of the message send.
   * @param {string} responseType - The type of the message to receive.
   * @param {Object} content - The payload to send.
   * @returns {Promise<Object>} - A promise with the response content/
   */
  request (requestType, responseType, content) {
    this.send(requestType, content)

    return new Promise(resolve => {
      const messageHandler = (response) => {
        const responseObj = JSON.parse(response)
        if (responseObj.type === responseType) {
          this.ws.removeEventListener('message', messageHandler)
          resolve(responseObj.content)
        }
      }
      this.ws.on('message', messageHandler)
    })
  }

  /**
   * A method to listen to a specific message type.
   * @param {string} type - The message type to listen to.
   * @param {connectorCallback} listener - The function to call.
   */
  listenToMsg (type, listener) {
    if (!(type in this.listeners.message)) {
      this.listeners.message[type] = []
    }

    this.listeners.message[type].push(listener)
  }
}

/**
 * An instance of Connector.
 * Use this to interact with this API.
 */
const inst = new Connector(path)
export default inst
