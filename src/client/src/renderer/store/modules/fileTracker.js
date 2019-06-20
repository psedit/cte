import Tab from '../../components/Tabs/tabType'
import connector from '../../../main/connector'
import { convertToJS, getFile, create } from '../../../main/pieceTable'

const state = {
  pieces: null,
  pieceTable: null,
  openFile: '',
  filePaths: '',
  tabs: []
}

const mutations = {
  /**
   * @param {Object} state
   * @param {pieceTable} pieceTable
   */
  updatePieces (state, pieceTable) {
    state.pieces = getFile(pieceTable)
  },

  /**
   *  Removes all tabs
   * @param {Object} state
   */
  clearTabs (state) {
    state.tabs = []
  },
  /**
   * @param {Object} state
   * @param {pieceTable} pieceTable
   */
  updatePieceTable (state, pieceTable) {
    state.pieceTable = pieceTable
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

    connector.send(
      'file-join',
      {
        'file_path': filePath
      }
    )

    connector.request(
      'file-content-request',
      'file-content-response',
      {
        'file_path': filePath,
        'start': 0,
        'length': -1
      }
    ).then((data) => {
      const pieceTable = convertToJS(data)
      store.dispatch('updatePieceTable', pieceTable)

      // fs.writeFile(filePath, data.file_content, (err) => {
      //   if (err) console.error(err)
      // })
    })
  },
  /**
   * Move to the tab before the tab with the given index.
   */
  prevTab (store, index) {
    if (index === 0) {
      index = store.state.tabs.length
    }
    store.dispatch('openFile', store.state.tabs[index - 1].filePath)
  },
  /**
   * Move to the tab after the tab with the given index.
   */
  nextTab (store, index) {
    if (index === store.state.tabs.length - 1) {
      index = -1
    }
    store.dispatch('openFile', store.state.tabs[index + 1].filePath)
  },
  /**
  * Updates pieces and piece table
  * @param {Object} store
  * @param {PieceTable} pieceTable
  */
  updatePieceTable (store, pieceTable) {
    store.commit('updatePieceTable', pieceTable)
    store.commit('updatePieces', pieceTable)
  },
  /**
   * Removes a tab from state and switches to a new tab if the tab was opened.
   * @param {Object} store vuex store
   * @param {Tab} tabToRemove the tab that needs to be removed
   */
  removeTab (store, tabToRemove) {
    if (tabToRemove.filePath === store.state.openFile) {
      const i = store.state.tabs.indexOf(tabToRemove)
      store.dispatch('prevTab', i)
    }
    store.commit('removeTab', tabToRemove)
  },
  /**
   *
   * @param {Object} store
   */
  clearTabs (store) {
    store.commit('updateOpenFile', '')
    store.commit('clearTabs')
    store.dispatch('updatePieceTable', create(''))
  },
  /**
   * Moves from the current tab to another tab in the given direction.
   * @param {Object} store vuex store
   * @param {Tab} direction 1 for moving to the next tab, 0 for to the previous
   */
  scrollTab (store, direction) {
    var i = 0
    for (let tab of store.state.tabs) {
      if (tab.filePath === store.state.openFile) {
        if (direction) {
          store.dispatch('nextTab', i)
        } else {
          store.dispatch('prevTab', i)
        }
        break
      }
      i++
    }
  }
}

export default {
  state,
  mutations,
  actions
}
