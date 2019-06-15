import { stringify } from 'querystring'

const uuid = require('uuid/v4')

/**
 * A text block
 * @typedef {Object} TextBlock
 * @property {boolean} open signals whether you can modify the TextBlock
 * @property {string[]} lines An array with text lines
 */

/**
 * @typedef {Object} Piece
 * @property {string} pieceID
 * @property {string} blockID
 * @property {number} start
 * @property {number} length
 */

/**
 * A piece table
 * Text file data structure consisting of the original file together with
 * so-called "edit-blocks" (see the TextBlock class), for which a table is
 * used to couple these seperate blocks into one single file.
 * @typedef {Object} PieceTable
 * @property {TextBlock[]} textBlocks
 * @property {Piece[]} table
 */

/**
 * @typedef {Object} Position
 * @property {number} index
 * @property {number} offset
 */

/**
 * @typedef {Object} Range
 * @property {number} start inclusive start
 * @property {number} end inclusive end
 */

/**
 * Returns a create function
 * @param {Function} UUID
 */
export function _create (UUID) {
  /**
   * Creates a new piece table object
   * @param {string|string[]} text
   * @returns {PieceTable} a piece table
   */
  return function c (text) {
    const lines = Array.isArray(text) ? text : text.split('\n')
    return {
      textBlocks: {
        '0': {
          open: false,
          lines: lines
        }
      },
      table: [
        { pieceID: UUID(), blockID: '0', start: 0, length: lines.length }
      ]
    }
  }
}

export let create = _create(uuid)

/**
 * Converts the python representation of the piece table to the js
 * represenation.
 * @param {Object} pyPiece
 * @param {TextBlock[]} pyPiece.textBlocks
 * @param {any[][]} pyPiece.table
 */
export function convert ({ textBlocks, table }) {
  return {
    textBlocks,
    table: table.map(([pieceID, blockID, start, length]) => {
      return {
        pieceID,
        blockID: blockID.toString(),
        start,
        length
      }
    })
  }
}

/**
 * Returns the length of the stitched file according to the table.
 * @param {Piece[]} table
 * @returns {number} the length
 */
export function len (table) {
  return table.reduce((total, curr) => total + curr.length, 0)
}

/**
 * Returns the corresponding piece index and piece offset
 * for a given file line. When line number is invalid returns 0, 0.
 * @param {Piece[]} table
 * @param {number} lineNumber the number where we need the piece of
 * @returns {Position}
 */
export function lineToTableIndex (table, lineNumber) {
  let pieceStart = 0
  for (let i = 0; i < table.length; i++) {
    const pieceLength = table[i].length
    if (lineNumber >= pieceStart && lineNumber < pieceStart + pieceLength) {
      return {
        index: i,
        offset: lineNumber - pieceStart
      }
    }
    pieceStart += pieceLength
  }
  return {
    index: 0,
    offset: 0
  }
}

/**
 * Returns the line at which the given piece (table index) begins within
 * the stitched file.
 * @param {Piece[]} table
 * @param {number} index table index
 * @returns {number} the start
 */
export function getStart (table, index) {
  return len(table.slice(0, index))
}

/**
 * @param {Piece[]} table
 * @param {number} lineNumber
 * @param {number} length
 * @returns {Range} a range of pieces which cover the given line range
 */
export function getRange (table, lineNumber, length) {
  const { index, offset } = lineToTableIndex(table, lineNumber)
  let rest = length - (table[index].length - offset)
  let lastOff = 1

  while (rest > 0 && index + lastOff < table.length) {
    rest -= table[index + lastOff].length
    lastOff++
  }

  return {
    start: index,
    end: index + lastOff - 1
  }
}

/**
 *
 * @param {Piece[]} table
 * @param {*} start
 * @param {*} length
 */
export function getLines (table, start, length) {}
