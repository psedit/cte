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

/**  Create a new empty file on the server.
 * Sends a message to the server, creating a new file
 *
 * @param {string} path path of file to be created.
 */
export function newFile (path) {
  this.fileChangeRequest('', path, '')
}

export function removeFile (path) {
  console.log('Removing ' + path)
  this.fileChangeRequest(path, '', '')
}

export function nameChange (pathToDir, oldName, newName) {
  // NOTE: pathToDir has to end on a  '/'
  console.log(`RENAMING pathToDir: ${pathToDir}, oldName: ${oldName}, newName: ${newName}`) // FIXME:
  this.locationChange(pathToDir + oldName, pathToDir + newName, '')
}

export function locationChange (oldPath, newPath) {
  this.fileChangeRequest(oldPath, newPath, '')
}
