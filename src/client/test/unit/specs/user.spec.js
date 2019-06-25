/* globals expect describe it */
import store from '../../../src/renderer/store/modules/user'
import testAction from './resources/testAction'

describe('user', () => {
  const { mutations, actions } = store

  const cursor = {
    username: 'jan',
    filepath: 'index.js',
    pieceID: '1',
    column: 1,
    row: 1
  }

  describe('mutations', () => {
    const { addCursor, removeCursor, emptyCursors } = mutations
    describe('addCursor', () => {
      it('should add cursor to the list of cursors', () => {
        const state = {
          cursors: [],
          username: 'piet'
        }
        addCursor(state, cursor)
        expect(state.cursors).to.deep.equal([cursor])
      })
      it('should not add its own username to the list', () => {
        const state = {
          cursors: [],
          username: 'jan'
        }
        addCursor(state, cursor)
        expect(state.cursors.length).to.equal(0)
      })
    })

    describe('removeCursor', () => {
      it('should filter a cursor from state.cursors based on its username and filepath', () => {
        const state = {
          cursors: [cursor]
        }
        removeCursor(state, cursor)
        expect(state.cursors.length).to.equal(0)
      })
      it('should not filter a cursor just on its username', () => {
        const state = {
          cursors: [cursor]
        }
        removeCursor(state, { cursor, filepath: '' })
        expect(state.cursors.length).to.equal(1)
      })
      it('should not filter a cursor just on its filepath', () => {
        const state = {
          cursors: [cursor]
        }
        removeCursor(state, { cursor, username: '' })
        expect(state.cursors.length).to.equal(1)
      })
    })
    describe('emptyCursors', () => {
      it('should remove all cursors', () => {
        const state = {
          cursors: [cursor]
        }
        emptyCursors(state)
        expect(state.cursors.length).to.equal(0)
      })
    })
  })

  describe('actions', () => {
    const { moveCursor } = actions
    describe('moveCursor', () => {
      const updatedCursor = {
        username: 'jan',
        filepath: 'index.js',
        pieceID: '1',
        column: 5,
        row: 5
      }
      it('should update the postion of the cursor', done => {
        testAction(
          moveCursor,
          updatedCursor,
          { cursors: [cursor] },
          [
            {
              type: 'updateCursor',
              payload: { index: 0, cursor: updatedCursor }
            }
          ],
          done
        )
      })
      it('should add a new cursor if cursor does not exist in this.cursors', done => {
        testAction(
          moveCursor,
          cursor,
          { cursors: [] },
          [
            {
              type: 'addCursor',
              payload: cursor
            }
          ],
          done
        )
      })
    })
  })
})
