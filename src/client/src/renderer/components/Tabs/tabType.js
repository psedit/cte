const path = require('path')

/** Definition for a tab */
class Tab {
  /**
  * @param {string} filePath a path to a document
  * @param {number} [line = 0] at which line number the client cursor was
  * @param {number} [ch = 0] at which character client cursor was
  */
  constructor (filePath, line = 0, ch = 0) {
    /**
     * A file path to a document
     * @type {string}
     * */
    this.filePath = filePath
    /**
     * A file name for a document
     * @type {string}
     */
    this.fileName = path.parse(filePath).base
    /**
     * A line number
     * @type {number}
     */
    this.line = line
    /**
     * A charachter position
     * @type {number}
     */
    this.ch = ch
  }
}
export default Tab
