/**
 * A text block
 * @typedef {Object} TextBlock
 * @property {boolean} open signals whether you can modify the TextBlock
 * @property {string[]} lines An array with text lines
 */

/**
 * A piece table
 * Text file data structure consisting of the original file together with
 * so-called "edit-blocks" (see the TextBlock class), for which a table is
 * used to couple these seperate blocks into one single file.
 * @typedef {Object} PieceTable
 * @property {TextBlock[]} TextBlocks
 * @property {int[][]} table
 */

/**
 * Creates a new piece table object
 * @param {string|string[]} text
 * @returns {PieceTable} a piece table
 */
export function createPieceTable (text) {
  const lines = Array.isArray(text) ? text : text.split('\n')
  return {
    TextBlocks: {
      '0': {
        open: false,
        lines: lines
      }
    },
    table: [[0, 0, lines.length]]
  }
}
