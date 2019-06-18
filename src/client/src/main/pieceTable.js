const uuid = require('uuid/v4')
const { insert, mergeLeft, clone, remove } = require('ramda')

/**
 * A text block
 * @typedef {Object} TextBlock
 * @property {boolean} open signals whether you can modify the TextBlock
 * @property {string[]} lines An array with text lines
 */

/**
 * @typedef {Object} Piece
 * @property {string} pieceID
 * @property {string|number} blockID
 * @property {number} start
 * @property {number} length
 */

/**
 * A piece table
 * Text file data structure consisting of the original file together with
 * so-called "edit-blocks" (see the TextBlock class), for which a table is
 * used to couple these seperate blocks into one single file.
 * @typedef {Object} PieceTable
 * @property {Object.<string, TextBlock>} textBlocks
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
 * @property {number} end exclusive end
 */

/**
 * @typedef {Object} Update
 * @property {string} filePath
 * @property {PieceTable} pieceTable the updated piece table
 * @property {TextBlock} changedBlock the block that is changed
 */

/**
 * @typedef FilePiece
 * @property {string} pieceID
 * @property {string[]} text the text of the file
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
      table: [{ pieceID: UUID(), blockID: 0, start: 0, length: lines.length, username: 'hans' }]
    }
  }
}

export let create = _create(uuid)

/**
 * Converts the python representation of the piece table to the js
 * represenation.
 * @param {Object} pyPiece
 * @returns {PieceTable} a pieceTable
 */
export function convertToJS (pyPieceTable) {
  return {
    textBlocks: pyPieceTable['block_list'].reduce(convertBlockToJS, {}),
    table: pyPieceTable['piece_table'].map(convertTableTojs)
  }
}

/**
 * @param {Object.<string, TextBlock>} obj
 * @param {any[]} block
 * @returns {Object.<string, TextBlock>} text blocks
 */
export function convertBlockToJS (obj, [blockID, closed, lines]) {
  obj = clone(obj)
  obj[blockID] = {
    open: !closed,
    lines
  }
  return obj
}

/**
 * @param {any[]} piece
 * @returns {Piece}
 */
export function convertTableTojs ([pieceID, blockID, start, length, username]) {
  return {
    pieceID,
    blockID,
    start,
    length,
    username
  }
}

/**
 * @param {Object.<string, TextBlock>} textBlocks
 * @param {Object} update
 * @returns {Update}
 */
export function convertChangeToJS (textBlocks, update) {
  return {
    filePath: update['file_path'],
    pieceTable: {
      textBlocks: convertBlockToJS(textBlocks, update['changed_block']),
      table: update['piece_table'].map(convertTableTojs)
    },
    changedBlock: convertBlockToJS({}, update['changed_block'])
  }
}

/**
 * @param {PieceTable} pieceTable
 * @returns {Object} an python piece table to send over sockets
 */
export function convertToPy ({ textBlocks, table }) {
  return {
    block_list: convertTextBlocksToPy({ textBlocks, table }),
    piece_table: table.map(convertPieceToPy)
  }
}

/**
 * @param {PieceTable} pieceTable
 * @returns {any[]} a block list
 */
export function convertTextBlocksToPy ({ textBlocks, table }) {
  return table.map(({ blockID }) => {
    return convertTextBlockToPy(textBlocks, blockID)
  })
}

/**
 * @param {Object.<string, TextBlock>} textBlocks
 * @param {number} blockID
 * @return {any[]} a block
 */
export function convertTextBlockToPy (textBlocks, blockID) {
  const { open, lines } = textBlocks[blockID]
  return [blockID, !open, lines]
}

/**
 * @param {Piece} piece
 * @returns {any[]} piece
 */
export function convertPieceToPy ({ pieceID, blockID, start, length }) {
  return [pieceID, blockID, start, length]
}

/**
 * Returns the length of the stitched file according to the table.
 * @param {Piece[]} table
 * @returns {number} the length of the table
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
    end: index + lastOff
  }
}

/**
 * @param {pieceTable} pieceTable
 * @param {string} pieceID
 * @returns {TextBlock} the corresponding TextBlock
 */
export function getBlock ({ textBlocks, table }, pieceID) {
  const piece = getPieceByPieceID(table, pieceID)
  return textBlocks[piece.blockID]
}

/**
 * @param {Piece[]} table
 * @param {string} pieceID
 * @returns {Piece}
 */
export function getPieceByPieceID (table, pieceID) {
  return table.find(x => x.pieceID === pieceID)
}

/**
 * @param {Piece[]} table
 * @param {string} pieceID
 * @returns {number}
 */
export function getPieceIndexByPieceID (table, pieceID) {
  return table.findIndex(x => x.pieceID === pieceID)
}

/**
 * Returns the new stitched file according to the piece table.
 * @param {PieceTable} pieceTable
 * @returns {string[]} the stiched file
 */
export function stitch ({ textBlocks, table }) {
  return [].concat(
    ...table.map(({ blockID, start, length }) =>
      textBlocks[blockID].lines.slice(start, start + length)
    )
  )
}

/**
 * @param {PieceTable} pieceTable
 * @param {string} pieceID
 * @returns {string[]} the text of the corresponding block
 */
export function getTextByPieceID ({ textBlocks, table }, pieceID) {
  const { blockID, start, length } = getPieceByPieceID(table, pieceID)
  const block = textBlocks[blockID]
  return block.lines.slice(start, start + length)
}

/**
 * @param {PieceTable}
 * @returns {FilePiece[]} a list of file pieces
 */
export function getFile ({ textBlocks, table }) {
  return table.map(({ pieceID, username }) => {
    return {
      pieceID,
      text: getTextByPieceID({ textBlocks, table }, pieceID),
      open: getBlock({ textBlocks, table }, pieceID).open,
      username
    }
  })
}

/**
 * @param {PieceTable} pieceTable
 * @param {number} pieceID
 * @param {string[]} lines
 * @return {PieceTable}
 */
export function edit ({ textBlocks, table }, pieceID, lines) {
  const index = getPieceIndexByPieceID(table, pieceID)
  const piece = table[index]
  const block = textBlocks[piece.blockID]

  const newPiece = {
    ...piece,
    length: lines.length
  }

  const newTable = clone(table)
  newTable[index] = newPiece
  const newBlock = mergeLeft({ lines }, block)
  const newTextblocks = clone(textBlocks)
  newTextblocks[piece.blockID] = newBlock

  return {
    table: newTable,
    textBlocks: newTextblocks
  }
}
