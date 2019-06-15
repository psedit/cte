/* globals expect describe it */
import {
  create,
  _create,
  len,
  lineToTableIndex,
  convert,
  getStart,
  getRange,
  getBLock,
  stich
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
  { pieceID: '5', blockID: '0', start: 5, length: 7 },
  { pieceID: '5', blockID: '0', start: 12, length: 19 }
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
    expect(create('').table[0].pieceID.length).to.equal(36)
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

const largePieceTable = {
  textBlocks: {
    '0': {
      open: false,
      lines: ['abc ', ' 123 ', ' 😀']
    },
    '1': {
      open: false,
      lines: ['xabc ', ' 2123 ', ' g😀', 'dfsasdfasdfasd']
    },
    '2': {
      open: false,
      lines: ['fabc ']
    }
  },
  table: [
    { pieceID: '1', blockID: '0', start: 0, length: 3 },
    { pieceID: '2', blockID: '1', start: 3, length: 3 },
    { pieceID: '3', blockID: '2', start: 6, length: 1 }
  ]
}

describe('getBlock', function () {
  it('should given an pieceID return the corresponding block', function () {
    expect(getBLock(largePieceTable, '2')).to.deep.equal({
      open: false,
      lines: ['xabc ', ' 2123 ', ' g😀', 'dfsasdfasdfasd']
    })
  })
})

describe('stich', function () {
  it('should return the complete document in the correct order', function () {
    expect(stich(largePieceTable)).to.deep.equal([
      'abc ',
      ' 123 ',
      ' 😀',
      'xabc ',
      ' 2123 ',
      ' g😀',
      'dfsasdfasdfasd',
      'fabc '
    ])
  })
})

// describe('getLines', function () {
//   const result = [
//     ' 2123 ',
//     ' g😀',
//     'dfsasdfasdfasd',
//     'fabc '
//   ]
//   console.log(getLines(largePieceTable, '0', 2, 4))

//   it('should get  list with the requested lines assembled from the piece present in the piece table', function () {
//     expect(getLines(largePieceTable, 1, 9)).to.deep.equal(result)
//   })
//   it('should get the first line if requested', function () {
//     expect(getLines(expected, 0, 1)).to.deep.equal(['abc '])
//   })
//   it('should return all lines until the last line, if length is -1', function () {
//     expect(getLines(largePieceTable, 4, -1)).to.deep.equal(result)
//   })
// })

// describe('stich', function () {

// })
