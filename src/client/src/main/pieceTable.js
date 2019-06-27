/**
 * @module pieceTable
 */

const uuid = require('uuid/v4')
const { mergeLeft, clone } = require('ramda')

/**
 * A text block that contains an array of text lines.
 * @typedef {Object} TextBlock a textblock object
 * @property {boolean} open signals whether you can modify the TextBlock
 * @property {string[]} lines An array with text lines
 */

/**
 * A piece containing information about how to read the buffer of a corresponding block.
 * @typedef {Object} Piece A piece object
 * @property {string} pieceID a unique piece ID
 * @property {string|number} blockID a block ID that corresponds to a block
 * @property {number} start where we should start reading in the text buffer of the block
 * @property {number} length the length of the text of the piece
 */

/**
 * A piece table
 * Text file data structure consisting of the original file together with
 * so-called "edit-blocks" (see the TextBlock class), for which a table is
 * used to couple these seperate blocks into one single file.
 * @typedef {Object} PieceTable a piece table object
 * @property {Object.<string, TextBlock>} textBlocks a dictionary of textblocks
 * @property {Piece[]} table a table containing pieces
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
 * An update object containing the update that was broadcast.
 * @typedef {Object} Update an update object
 * @property {string} filePath In which file the update happened
 * @property {PieceTable} pieceTable the updated piece table
 * @property {TextBlock} changedBlock the block that is changed
 */

/**
 * A FilePiece object that can be rendered via an editor piece.
 * @typedef {Object} FilePiece a file piec object
 * @property {string} pieceID the piece ID of the corresponding piece
 * @property {string[]} text the text of the file
 * @property {boolean} open whether the block is open
 * @property {string} username username of the person that locked the piece
 */

/**
 * Returns a create functio that can create a PieceTable.
 * @param {Function} UUID a function that can create an UUID.
 */
export function _create (UUID) {
  /**
   * Creates a new piece table object
   * @param {string|string[]} text The text we want in the piece table
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
      table: [{
        pieceID: UUID(),
        blockID: 0,
        start: 0,
        length: text.length === 0 ? 0 : lines.length,
        username: 'hans'
      }]
    }
  }
}

export let create = _create(uuid)

/**
 * Converts the python representation of the piece table to the js
 * represenation.
 * @param {Object} pyPiece The python representation of an piece table
 * @returns {PieceTable} a pieceTable
 */
export function convertToJS (pyPieceTable) {
  return {
    textBlocks: pyPieceTable['block_list'].reduce(convertBlockToJS, {}),
    table: pyPieceTable['piece_table'].map(convertPieceToJS)
  }
}

/**
 * Converts an individual block from python to javascript and adds it to obj.
 * @param {Object.<string, TextBlock>} obj A TextBlock dictionary can also be an empty object
 * @param {any[]} block The python representation of an textblock
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
 * Convert a python piece to a js piece.
 * @param {any[]} piece The python representation of a piece
 * @returns {Piece} the js representation of a piece.
 */
export function convertPieceToJS ([pieceID, blockID, start, length, username]) {
  return {
    pieceID,
    blockID,
    start,
    length,
    username
  }
}

/**
 * Converts the indivual properties of a python update to js.
 * @param {Object.<string, TextBlock>} textBlocks A Textblock dictionary
 * @param {Object} update the python update object
 * @returns {Update} A js Update object
 */
export function convertChangeToJS (textBlocks, update) {
  return {
    filePath: update['file_path'],
    pieceTable: {
      textBlocks: update['changed_blocks'].reduce(convertBlockToJS, textBlocks),
      table: update['piece_table'].map(convertPieceToJS)
    },
    changedBlocks: update['changed_blocks'].reduce(convertBlockToJS, {})
  }
}

/**
 * Converts a javascript piecetable to python
 * @param {PieceTable} pieceTable A pieceTable to convert
 * @returns {Object} an python piece table to send over sockets
 */
export function convertToPy ({ textBlocks, table }) {
  return {
    block_list: convertTextBlocksToPy({ textBlocks, table }),
    piece_table: table.map(convertPieceToPy)
  }
}

/**
 * Convert the blocks in a piecetable to python.
 * @param {PieceTable} pieceTable A pieceTable
 * @returns {any[]} a block list
 */
export function convertTextBlocksToPy ({ textBlocks, table }) {
  return table.map(({ blockID }) => {
    return convertTextBlockToPy(textBlocks, blockID)
  })
}

/**
 * Convert individual javascript textblock to python
 * @param {Object.<string, TextBlock>} textBlocks
 * @param {number} blockID The ID of a block
 * @return {any[]} a block
 */
export function convertTextBlockToPy (textBlocks, blockID) {
  const { open, lines } = textBlocks[blockID]
  return [blockID, !open, lines]
}

/**
 * Convert a single pice from javascript to python.
 * @param {Piece} piece A piece to convert
 * @returns {any[]} piece
 */
export function convertPieceToPy ({ pieceID, blockID, start, length }) {
  return [pieceID, blockID, start, length]
}

/**
 * Returns the length of the stitched file according to the table.
 * @param {Piece[]} table A table containing pieces
 * @returns {number} the length of the table
 */
export function len (table) {
  return table.reduce((total, curr) => total + curr.length, 0)
}

/**
 * Return A and B in order.
 * @param {Object} A
 * @param {Object} B
 */
export function indexOffsetRangeSort (A, B) {
  const comp = indexOffsetCompare(A, B)
  if (comp > 0) {
    return [ B, A ]
  } else {
    return [ A, B ]
  }
}

/**
 * Determine the order of A and B.
 * @param {Object} A
 * @param {Object} B
 */
export function indexOffsetCompare (A, B) {
  if (A.piece < B.piece || (A.piece === B.piece && A.line < B.line)) {
    return -1
  } else if (A.piece > B.piece || (A.piece === B.piece && A.line > B.line)) {
    return 1
  } else {
    return 0
  }
}

/**
 * Make a new piece based on selected lines.
 * @param {PieceTable} table A piece table
 * @param {number} idxA
 * @param {number} offsetA
 * @param {number} idxB
 * @param {number} offsetB
 */
export function rangeToAnchoredLength (table, idxA, offsetA,
  idxB, offsetB) {
  let startPiece, endPiece
  if (idxA < idxB || (idxA === idxB && offsetA <= offsetB)) {
    startPiece = { piece: idxA, offset: offsetA }
    endPiece = { piece: idxB, offset: offsetB }
  } else {
    startPiece = { piece: idxB, offset: offsetB }
    endPiece = { piece: idxA, offset: offsetA }
  }

  let interLines = 0
  for (let i = startPiece.piece; i < endPiece.piece; i++) {
    interLines += table.table[i].length
  }

  return {
    index: startPiece.piece,
    offset: startPiece.offset,
    length: interLines - startPiece.offset + endPiece.offset + 1
  }
}

/**
 * Compute number of lines between two locations in the piece table
 * @param {Piece[]} table a piece table
 * @param {Piece} startpiece the piece where to start counting
 * @param {int} startoffset the offset from the start piece
 * @param {piece} endpiece the piece where to stop counting
 * @param {int} endoffset the offset from the end piece
 */
export function lengthBetween (table, startpiece, startoffset,
  endpiece, endoffset) {
  let accumulator = 0
  for (let i = getPieceIndexByPieceID(table, startpiece);
    i < getPieceByPieceID(table, endpiece); i++) {
    accumulator += table[i].length
  }
  return accumulator - startoffset + endoffset + 1
}

/**
 * Returns the corresponding piece index and piece offset
 * for a given file line. When line number is invalid returns 0, 0.
 * @param {Piece[]} table a piece table
 * @param {number} lineNumber the number where we need the piece of
 * @returns {Position} the postion in table index
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
 * @param {Piece[]} table a piece table
 * @param {number} index table index
 * @returns {number} the start
 */
export function getStart (table, index) {
  return len(table.slice(0, index))
}

/**
 * Calculates which pieces cover a certain line range
 * @param {Piece[]} table a piece table
 * @param {number} lineNumber the line number where to start the range
 * @param {number} length the amount of lines in the range
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
 * Determine the start and end pieces based on ID's.
 * @param {Piece[]} table a piece table
 * @param {PieceID} startPieceID the piece ID of the first piece in the range
 * @param {PieceID} endPieceID the piece ID of the last piece in the range
 * @returns {Range} a range of pieces which cover the given piece ID's
 */
export function getRangeById (table, startPieceID, endPieceID) {
  const startPiece = getPieceIndexByPieceID(startPieceID)
  const endPiece = getPieceIndexByPieceID(endPieceID)

  return {
    start: startPiece,
    end: endPiece
  }
}

/**
 * Get a block by pieceID
 * @param {pieceTable} pieceTable a piece table
 * @param {string} pieceID the piece ID of the block
 * @returns {TextBlock} the corresponding TextBlock
 */
export function getBlock ({ textBlocks, table }, pieceID) {
  const piece = getPieceByPieceID(table, pieceID)
  return textBlocks[piece.blockID]
}

/**
 * Return a piece with corresponding ID.
 * @param {Piece[]} table a piece table
 * @param {string} pieceID the piece ID of the piece
 * @returns {Piece} the corresponding piece
 */
export function getPieceByPieceID (table, pieceID) {
  return table.find(x => x.pieceID === pieceID)
}

/**
 * Get the piece index based on piece ID.
 * @param {Piece[]} table a piece table
 * @param {string} pieceID the piece id of the piece
 * @returns {number} the index of the corresponding piece
 */
export function getPieceIndexByPieceID (table, pieceID) {
  return table.findIndex(x => x.pieceID === pieceID)
}

/**
 * Returns the new stitched file according to the piece table.
 * @param {PieceTable} pieceTable a piece table
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
 * Get the text from a piece based on the PieceID
 * @param {PieceTable} pieceTable a piece table
 * @param {string} pieceID a piece ID that corresponds to a block of text
 * @returns {string[]} the text of the corresponding block
 */
export function getTextByPieceID ({ textBlocks, table }, pieceID) {
  const { blockID, start, length } = getPieceByPieceID(table, pieceID)
  const block = textBlocks[blockID]
  return block.lines.slice(start, start + length)
}

/**
 * Get file pieces from the piecetable.
 * @param {PieceTable} a piece table
 * @returns {FilePiece[]} a list of file pieces
 */
export function getFile ({ textBlocks, table }) {
  return table.filter(({ length }) => length > 0).map(({ pieceID, username }) => {
    return {
      pieceID,
      text: getTextByPieceID({ textBlocks, table }, pieceID),
      open: getBlock({ textBlocks, table }, pieceID).open,
      username
    }
  })
}

/**
 * Computes a new piece table based on lines changed in a certain piece.
 * @param {PieceTable} pieceTable a piece table
 * @param {number} pieceID the piece ID of the piece that contains the updated text
 * @param {string[]} lines the updated text of the piece
 * @return {PieceTable} an updated piece table.
 */
export function edit ({ textBlocks, table }, pieceID, lines) {
  const index = getPieceIndexByPieceID(table, pieceID)
  const piece = table[index]
  const block = textBlocks[piece.blockID]

  const newPiece = {
    ...piece,
    length: lines.length
  }

  // Ensure we make a deep copy of the table and textblocks
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
