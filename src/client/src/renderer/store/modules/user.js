/**
 * @typedef Cursor
 * @property {string} username
 * @property {string} pieceID
 * @property {number} ch the character index in the line
 * @property {number} line the line index in the piece
 */

const state = {
  username: '',
  cursors: []
}

const mutations = {
  /**
   * Changes state.username to username
   * @param {Object} state
   * @param {string} username
   */
  changeUsername (state, username) {
    state.username = username
  },
  /**
   * Adds cursor to the end of state.cursors
   * @param {Object} state
   * @param {Cursor} cursor
   */
  addCursor (state, cursor) {
    if (cursor.username === state.username) return
    state.cursors = [...state.cursors, cursor]
  },
  /**
   * Updates the value of the cursor at state.cursors at the index
   * @param {Object} state
   * @param {Object} payload
   * @param {number} payload.index
   * @param {Cursor} payload.cursor
   */
  updateCursor (state, { index, cursor }) {
    state.cursors[index] = cursor
  },
  removeCursor (state, { username, filepath }) {
    state.cursors = state.cursors.filter(cursor => cursor.username !== username && cursor.filepath !== filepath)
  }
}

const actions = {
  moveCursor (store, cursor) {
    const index = store.state.cursors.findIndex(
      ({ username, filepath }) =>
        cursor.username === username && cursor.filepath === filepath
    )
    if (index === -1) {
      store.commit('addCursor', cursor)
    } else {
      store.commit('updateCursor', { index, cursor })
    }
  }
}

export default {
  state,
  mutations,
  actions
}
