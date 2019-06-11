const fs = require('fs')
const state = {
  code: '',
  openedFile: '',
  filePaths: '',
  tabs: []
}

const mutations = {
  updateCode (state, newCode) {
    state.code = newCode
  },
  /** Adds a tab to state
   * @param {Object} state
   * @param {string} newTab
   */
  addTab (state, newTab) {
    if (!state.tabs.includes(newTab)) {
      state.tabs = [...state.tabs, newTab]
    }
  },
  /** Removes a tab from state
   * @param {Object} state
   * @param {string} tabToRemove
   */
  removeTab (state, tabToRemove) {
    state.tabs.filter(x => x !== tabToRemove)
  },
  /** Updates the filepaths
   * @param {Object} state
   * @param {Object[]} filePaths
   */
  updateFiles (state, filePaths) {
    state.filePaths = filePaths
  }
}

const actions = {
  /** Opens a file from the root of the project, and updates the code.
   * Also changes the openedFile state. Add the file to the tabs.
   * @param {Object} state
   * @param {string} filePath
   */
  openFile (state, filePath) {
    state.openedFile = filePath
    state.commit('addTab', filePath)
    fs.readFile(filePath.substring(0, filePath.length - 1), 'utf8', (err, data) => {
      if (err) {
        console.error(err)
        state.commit('updateCode', `Something went wrong: ${err}`)
      }
      state.commit('updateCode', data)
    })
  },
  updateCodeAction (state, newCode) {
    state.commit('updateCode', newCode)
  }
}

export default {
  state,
  mutations,
  actions
}
