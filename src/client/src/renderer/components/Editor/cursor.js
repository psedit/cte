import { getRandomColor } from './RandomColor'

/**
 * @module cursor
 * @desc Converts server representation to client representation.
 */

/**
 * @typedef Cursor
 * @property {string} username
 * @property {string} filepath
 * @property {string} pieceID
 * @property {number} ch the character index in the line
 * @property {number} line the line index in the piece
 * @property {Object} color the color of the cursor
 */

/**
 * Converts a python cursor to the editor representation
 * @param {Object} pyCursor
 * @returns {Cursor}
 */
export default function convert ({
  username,
  piece_id: pieceID,
  file_path: filepath,
  offset: line,
  column: ch
}) {
  return {
    username,
    filepath,
    pieceID,
    line,
    ch,
    color: getRandomColor(username)
  }
}
