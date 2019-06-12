import Tab from '../../components/Tabs/tabType'
const fs = require('fs')

const state = {
  code: '',
  openFile: '',
  filePaths: '',
  tabs: []
}

const mutations = {
  updateCode (state, newCode) {
    state.code = newCode
  },
  /**
   * Adds a tab to state
   * @param {Object} state vuex state
   * @param {string} filePath the filepath that needs to be added as tab
   */
  addTab (state, filePath) {
    if (state.tabs.every(x => x.filePath !== filePath)) {
      const newTab = new Tab(filePath)
      state.tabs = [...state.tabs, newTab]
    }
  },
  removeTab (state, tabToRemove) {
    state.tabs = state.tabs.filter(x => x.filePath !== tabToRemove.filePath)
  },
  /**
   * Updates the filepaths
   * @param {Object} state
   * @param {Object[]} filePaths
   */
  updateFiles (state, filePaths) {
    state.filePaths = filePaths
  },
  updateOpenFile (state, filePath) {
    state.openFile = filePath
  }
}

const actions = {
  /**
   * Opens a file from the root of the project, and updates the code.
   * Also changes the openedFile state. Add the file to the tabs.
   * @param {Object} state vuex state
   * @param {string} filePath the file path to document to be opened
   */
  openFile (state, filePath) {
    state.commit('updateOpenFile', filePath)
    state.commit('addTab', filePath)
    fs.readFile(filePath.substring(0, filePath.length - 1), 'utf8', (err, data) => {
      if (err) {
        console.error(err)
        state.commit('updateCode', `Something went wrong: ${err}`)
      }
      state.commit('updateCode', data)
    })
  },
  /**
   * Removes a tab from state and switches to a new tab if the tab was opened.
   * @param {Object} state vuex state
   * @param {Tab} tabToRemove the tab that needs to be removed
   */
  removeTab (state, tabToRemove) {
    console.log(state.fileTracker.openFile)
    if (tabToRemove.filePath === state.openFile) {
      if (state.tabs.length === 1) {
        console.log('test')
      } else {
        const i = state.tabs.indexOf(tabToRemove)
        state.dispatch('openFile', (state.tabs[(i - 1) % state.tabs.length].filePath))
      }
    }
    state.commit('removeTab', tabToRemove)
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
