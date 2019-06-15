/* globals expect describe it */
import { createPieceTable } from '../../../src/main/pieceTable'

describe('createPieceTable', function () {
  const expected = {
    TextBlocks: {
      '0': {
        open: false,
        lines: ['abc ', ' 123 ', ' 😀']
      }
    },
    table: [[0, 0, 3]]
  }
  it('should create a new Piece Table given a string', () => {
    const testString = 'abc \n 123 \n 😀'

    const result = createPieceTable(testString)
    expect(result).to.deep.equal(expected)
  })

  it('should create a new Piece Table given an array of strings', () => {
    const testArr = [
      'abc ',
      ' 123 ',
      ' 😀'
    ]
    const result = createPieceTable(testArr)
    expect(result).to.deep.equal(expected)
  })
})
