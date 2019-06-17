/* globals expect describe it */
import {
  create,
  _create,
  len,
  lineToTableIndex,
  convertToJS,
  convertToPy,
  convertChangeToJS,
  getStart,
  getRange,
  getBlock,
  stitch,
  getTextByPieceID,
  getFile,
  edit
} from '../../../src/main/pieceTable'

const expected = {
  textBlocks: {
    '0': {
      open: false,
      lines: ['abc ', ' 123 ', ' 😀']
    }
  },
  table: [{ pieceID: 'kat', blockID: 0, start: 0, length: 3 }]
}

const expectedPy = {
  block_list: [[0, true, expected.textBlocks[0].lines]],
  piece_table: [['kat', 0, 0, 3]]
}

const table = [
  { pieceID: '5', blockID: 0, start: 0, length: 5 },
  { pieceID: '5', blockID: 0, start: 5, length: 7 },
  { pieceID: '5', blockID: 0, start: 12, length: 19 }
]

describe('create', function () {
  const UUID = () => 'kat'
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

describe('convertToJS', function () {
  it('should convert the python representation of the piece table to the js represenation', function () {
    expect(convertToJS(expectedPy)).to.deep.equal(expected)
  })
})

describe('convertToPy', function () {
  it('should convert the javascript representation of the piece table to the py represenation', function () {
    expect(convertToPy(expected)).to.deep.equal(expectedPy)
  })
})

describe('convertChangeToJS', function () {
  it('should convert the file-piece-table-change-broadcast to an update type', function () {
    const res = convertChangeToJS(
      {},
      {
        file_path: 'test.js',
        piece_table: expectedPy['piece_table'],
        changed_block: expectedPy['block_list'][0]
      }
    )
    expect(res.filePath).to.equal('test.js')
    expect(res.pieceTable).to.deep.equal(expected)
    expect(res.changedBlock).to.deep.equal(expected['textBlocks'])
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
      end: 2
    })
  })

  it('should return 0, 0 at index 0 length 0', function () {
    expect(getRange(table, 0, 0)).to.deep.equal({
      start: 0,
      end: 1
    })
  })

  it('should return all blocks if range is larger then piece range', function () {
    expect(getRange(table, 0, 100)).to.deep.equal({
      start: 0,
      end: 3
    })
  })

  it('should return all blocks if range is invalid', function () {
    expect(getRange(table, 100, 100)).to.deep.equal({
      start: 0,
      end: 3
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
    { pieceID: '1', blockID: '0', start: 1, length: 2 },
    { pieceID: '2', blockID: '1', start: 2, length: 1 },
    { pieceID: '3', blockID: '2', start: 0, length: 1 }
  ]
}

describe('getBlock', function () {
  it('should given an pieceID return the corresponding block', function () {
    expect(getBlock(largePieceTable, '2')).to.deep.equal({
      open: false,
      lines: ['xabc ', ' 2123 ', ' g😀', 'dfsasdfasdfasd']
    })
  })
})

describe('getText', function () {
  it('should return the text of the block given an pieceID', function () {
    expect(getTextByPieceID(largePieceTable, '1')).to.deep.equal([
      ' 123 ',
      ' 😀'
    ])
  })
})

describe('stitch', function () {
  it('should return the complete document in the correct order', function () {
    expect(stitch(largePieceTable)).to.deep.equal([
      ' 123 ',
      ' 😀',
      ' g😀',
      'fabc '
    ])
  })
})

describe('getFile', function () {
  it('should return the file', function () {
    expect(getFile(largePieceTable)).to.deep.equal([
      { pieceID: '1', text: [' 123 ', ' 😀'], open: false },
      { pieceID: '2', text: [' g😀'], open: false },
      { pieceID: '3', text: ['fabc '], open: false }
    ])
  })
})

describe('edit', function () {
  it('should return an edited piece table', function () {
    expect(getFile(edit(largePieceTable, '3', ['kaas', 'hoi']))).to.deep.equal([
      { pieceID: '1', text: [' 123 ', ' 😀'], open: false },
      { pieceID: '2', text: [' g😀'], open: false },
      { pieceID: '3', text: ['kaas', 'hoi'], open: false }
    ])
    expect(getFile(edit(largePieceTable, '1', ['abc ', ' 123 ', ' 😀aaa']))).to.deep.equal([
      { pieceID: '1', text: [' 123 ', ' 😀aaa'], open: false },
      { pieceID: '2', text: [' g😀'], open: false },
      { pieceID: '3', text: ['fabc '], open: false }
    ])
  })
})
