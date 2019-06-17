/** Sends message to the server indicating a file change.
  * 
  * @param {string} old_path empty if creating new file
  * @param {string} new_path empty if removing file
  * @param {string} file_content the content of the file 
  */
export function fileChangeRequest (old_path, new_path, file_content) {
  connector.addEventListener('open', () => {
    connector.send('file-change', {
      old_path,
      new_path,
      file_content
    })
  })
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
  console.log(path)
  // this.fileChangeRequest(path, '', '')
}

export function nameChange (path_to_dir, old_name, new_name) {
  // NOTE: path_to_dir has to end on a  '/' 
  this.locationChange(path_to_dir + old_name, path_to_dir + new_name, '')
}

export function locationChange (old_path, new_path) {
  this.fileChangeRequest(old_path, new_path, '')
}