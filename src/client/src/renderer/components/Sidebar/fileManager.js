/**
 * Sends messages to the server when changes are made to the files.
 *
 * @module fileManager
 */

import connector from '../../../main/connector'

/** Sends message to the server indicating a file change.
  *
  * @param {string} oldPath empty if creating new file
  * @param {string} newPath empty if removing file
  * @param {string} fileContent the content of the file (only used for
  *                             adding non-empty files to server)
  */
export function fileChangeRequest (oldPath, newPath, fileContent) {
  /**
   * Send a file-change message to server.
   */
  function sendMessage () {
    connector.send('file-change', {
      old_path: oldPath,
      new_path: newPath,
      file_content: fileContent
    })
  }

  /* If connection is not open, first open the websocket. */
  if (connector.isOpen()) {
    sendMessage()
  } else {
    connector.addEventListener('open', () => {
      sendMessage()
    })
  }
}

/**
 * Create a new empty file on the server.
 * Sends a message to the server, creating a new file
 *
 * @param {string} path path of file to be created.
 */
export function newFile (path) {
  fileChangeRequest('', path, '')
}

/**
 * Upload (locally existing) file to server.
 *
 * @param {string} path location of uploaded file on server
 * @param {string} content content of file
 */
export function uploadFile (path, content) {
  fileChangeRequest('', path, content)
}

/**
 * Remove file from server.
 *
 * @param {string} path path on server of file or directory to be deleted
 */
export function removeItem (path) {
  fileChangeRequest(path, '', '')
}

/**
 * Change name of file.
 *
 * @param {string} pathToDir path to directory in which file is located (has to end on '/')
 * @param {string} oldName current name of file
 * @param {string} newName new name of file
 */
export function nameChange (pathToDir, oldName, newName) {
  locationChange(pathToDir + oldName, pathToDir + newName, '')
}

/**
 * Change location of file.
 *
 * @param {string} oldPath old path of file
 * @param {string} newPath new path of file
 */
export function locationChange (oldPath, newPath) {
  fileChangeRequest(oldPath, newPath, '')
}
