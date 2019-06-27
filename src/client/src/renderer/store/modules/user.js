import Vue from 'vue'
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
    Vue.set(state, 'cursors', [...state.cursors, cursor])
  },
  /**
   * Updates the value of the cursor at state.cursors at the index
   * @param {Object} state
   * @param {Object} payload
   * @param {number} payload.index
   * @param {Cursor} payload.cursor
   */
  updateCursor (state, { index, cursor }) {
    Vue.set(state.cursors, index, cursor)
  },
  /**
   * Removes a cursor with a certain username and filepath from state.cursors
   * @param {Object} state
   * @param {Cursor} cursor
   */
  removeCursor (state, { username, filepath }) {
    Vue.set(state, 'cursors', state.cursors.filter(cursor => cursor.username !== username && cursor.filepath !== filepath))
  },
  /**
   * Removes all cursors
   */
  emptyCursors (state) {
    state.cursors.splice(0)
  }
}

const actions = {
  /**
   * Updates cursor if it exists, otherwhise adds a new cursor
   * @param {Object} store
   * @param {Cursor} cursor
   */
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
