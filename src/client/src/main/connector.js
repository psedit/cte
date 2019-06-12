const WebSocket = require('ws')
const uuid = require('uuid/v4')

// FIXME: Change path to server path.
// const path = new URL('ws://segfault.party:12345')
const path = new URL('ws://bami.party:12345')

// const path = new URL('ws://localhost:8080')

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
   * Creates a connection and setups listeners.
   * @param {string | URL} path - The path to the websocket server.
   */
  constructor (path) {
    // Setup websocket
    this.ws = new WebSocket(path, {
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
export default new Connector(path)
