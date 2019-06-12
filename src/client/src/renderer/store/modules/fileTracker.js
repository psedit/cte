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
   * @param {Object} store vuex store
   * @param {string} filePath the file path to document to be opened
   */
  openFile (store, filePath) {
    store.commit('updateOpenFile', filePath)
    store.commit('addTab', filePath)
    fs.readFile(filePath.substring(0, filePath.length - 1), 'utf8', (err, data) => {
      if (err) {
        console.error(err)
        store.commit('updateCode', `Something went wrong: ${err}`)
      }
      store.commit('updateCode', data)
    })
  },
  /**
   * Removes a tab from state and switches to a new tab if the tab was opened.
   * @param {Object} store vuex store
   * @param {Tab} tabToRemove the tab that needs to be removed
   */
  removeTab (store, tabToRemove) {
    if (tabToRemove.filePath === store.state.openFile) {
      if (store.state.tabs.length === 1) {
        store.commit('updateOpenFile', '')
        // FIXME: hide the editor if last file is removed
        store.commit('updateCode', 'Fix even pls dat de editor verdwijnt. (v-if)')
      } else {
        const i = store.state.tabs.indexOf(tabToRemove)
        store.dispatch('openFile', store.state.tabs[(i - 1) % store.state.tabs.length].filePath)
      }
    }
    store.commit('removeTab', tabToRemove)
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
  // readLocalDirTree (root) {
  //   /* Loop over all files in current directory and add
  //    * object to files array, storing the name and type
  //    * (either directory or file) of the file.
  //    * For sorting purposes, first push all directories
  //    * and then all other files. */
  //   fs.readdirSync(currFolder).forEach(file => {
  //     if (fs.lstatSync(currFolder + file).isDirectory()) {
  //       files.push({name: file, type: 'dir', path: `${currFolder}${file}/`})
  //     }
  //   })
  //
  //   fs.readdirSync(currFolder).forEach(file => {
  //     if (!fs.lstatSync(currFolder + file).isDirectory()) {
  //       files.push({name: file, type: 'file', path: `${currFolder}${file}/`})
  //     }
  //   })
  // }
