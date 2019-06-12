const fs = require('fs')
const state = {
  code: '',
  openedFile: '',
  filePaths: [],
  tabs: ['']
}

const mutations = {
  updateCode (state, newCode) {
    state.code = newCode
  },
  /** Adds a tab to state
   * @param {Object} state vuex state
   * @param {string} newTab the tab that need to be added
   */
  addTab (state, newTab) {
    if (!state.tabs.includes(newTab)) {
      state.tabs = [...state.tabs, newTab]
    }
  },
  /** Removes a tab from state
   * @param {Object} state vuex state
   * @param {string} tabToRemove the tab that needs to be removed
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
   * @param {Object} state vuex state
   * @param {string} filePath the file path to document to be opened
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
  },
  /** Updates the filepaths
   * @param {Object} state
   * @param {Object[]} filePaths
   */
  updateFilesAction (state, filePaths) {
    state.commit('updateFiles', filePaths)
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
