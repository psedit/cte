const path = require('path')

/** Definition for a tab */
class Tab {
  /**
  * @param {string} filePath a path to a document
  * @param {number} [line = 0] at which line number the client cursor was
  * @param {number} [ch = 0] at which charcter client cursor was
  */
  constructor (filePath, line = 0, ch = 0) {
    /** @type {string} a file path to a document */
    this.filePath = filePath
    /** @type {string} a file name for a document */
    this.fileName = path.parse(filePath).base
    /** @type {number} a line number */
    this.line = line
    /** @type {number} a charchter position */
    this.ch = ch
  }
}
export default Tab
