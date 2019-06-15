/* globals expect describe it */
import {
  create,
  _create,
  len,
  lineToTableIndex,
  convert,
  getStart,
  getRange
} from '../../../src/main/pieceTable'

const expected = {
  textBlocks: {
    '0': {
      open: false,
      lines: ['abc ', ' 123 ', ' 😀']
    }
  },
  table: [{ pieceID: '5', blockID: '0', start: 0, length: 3 }]
}

const table = [
  { pieceID: '5', blockID: '0', start: 0, length: 5 },
  { pieceID: '5', blockID: '0', start: 0, length: 7 },
  { pieceID: '5', blockID: '0', start: 0, length: 19 }
]

describe('create', function () {
  const UUID = () => '5'
  const c = _create(UUID)
  it('should create a new Piece Table given a string', () => {
    const testString = 'abc \n 123 \n 😀'
    expect(c(testString)).to.deep.equal(expected)
  })

  it('should create a new Piece Table given an array of strings', () => {
    const testArr = ['abc ', ' 123 ', ' 😀']
    expect(c(testArr)).to.deep.equal(expected)
  })

  it('should generate an UUID', function () {
    const e = ''
    expect(create(e).table[0].pieceID.length).to.equal(36)
  })
})

describe('convert', function () {
  it('should convert the python representation of the piece table to the js represenation', function () {
    expect(
      convert({
        ...expected,
        table: [['5', 0, 0, 3]]
      })
    ).to.deep.equal(expected)
  })
})

describe('len', function () {
  it('should calculate the length of the entire piece table', function () {
    expect(len(table)).to.equal(31)
  })
})

describe('lineToTableIndex', function () {
  it('should return the position in the piece table according to the line number', function () {
    expect(lineToTableIndex(table, 8)).to.deep.equal({
      index: 1,
      offset: 3
    })
    expect(lineToTableIndex(table, 2)).to.deep.equal({
      index: 0,
      offset: 2
    })
  })
  it('should return 0, 0 if line number is invalid ', function () {
    expect(lineToTableIndex(table, 100)).to.deep.equal({
      index: 0,
      offset: 0
    })
  })
})

describe('getStart', function () {
  it('should return the line at which the given piece begins.', function () {
    expect(getStart(table, 2)).to.equal(12)
  })
  it('should return 0 if the index is 0', function () {
    expect(getStart(table, 0)).to.equal(0)
  })
})

describe('getRange', function () {
  it('should return a range of pieces which cover the given line range', function () {
    expect(getRange(table, 1, 6)).to.deep.equal({
      start: 0,
      end: 1
    })
  })

  it('should return 0, 0 at index 0 length 0', function () {
    expect(getRange(table, 0, 0)).to.deep.equal({
      start: 0,
      end: 0
    })
  })

  it('should return all blocks if range is larger then piece range', function () {
    expect(getRange(table, 0, 100)).to.deep.equal({
      start: 0,
      end: 2
    })
  })

  it('should return all blocks if range is invalid', function () {
    expect(getRange(table, 100, 100)).to.deep.equal({
      start: 0,
      end: 2
    })
  })
})