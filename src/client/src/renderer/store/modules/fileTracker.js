import Tab from '../../components/Tabs/tabType'
import connector from '../../../main/connector'
import { convertToJS, getFile, create, lengthBetween } from '../../../main/pieceTable'

const state = {
  pieces: null,
  pieceTable: null,
  openFile: '',
  filePaths: '',
  tabs: []
}

const mutations = {
  serverURLChange (store) {
  },
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
  removeTab (state, tabPath) {
    state.tabs = state.tabs.filter(x => x.filePath !== tabPath)
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
  },
  /**
   * Renames a given tab.
   * @param {Object} store vuex store
   * @param {Object} payload a key array with keys pathToDir, the path to the
   * directory in which the file is located (has to end on '/'), oldName, the
   * current name of the file, and newName, the new name of the file.
   * They are stored in one object because this can't be done differently for mutations.
   */
  renameTab (state, payload) {
    if (payload.pathToDir + payload.oldName === state.openFile) {
      state.openFile = payload.pathToDir + payload.newName
    }
    for (let tab of state.tabs) {
      if (tab.fileName === payload.oldName) {
        tab.filePath = payload.pathToDir + payload.newName
        tab.fileName = payload.newName
        break
      }
    }
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
  serverURLChange (store) {
    store.commit('serverURLChange')
    store.dispatch('clearTabs')
  },
  /**
   * Removes a tab from state and switches to a new tab if the tab was the
   * currently opened tab. The changes made to the tab are also saved, and
   * after closing the user is removed from the list of users in a tab.
   * @param {Object} store vuex store
   * @param {Tab} tabToRemove the tab that needs to be removed
   */
  removeTab (store, tabToRemove) {
    connector.send('file-leave', {
      file_path: store.state.openFile,
      force_exit: 1
    })
    if (tabToRemove.filePath === store.state.openFile) {
      if (store.state.tabs.length === 1) {
        store.commit('updateOpenFile', '')
        store.dispatch('updatePieceTable', create(''))
      } else {
        const i = store.state.tabs.indexOf(tabToRemove)
        store.dispatch('prevTab', i)
      }
    }
    store.commit('removeTab', tabToRemove.filePath)
  },
  /**
   * Removes a tab from state and switches to a new tab if the tab was opened.
   * This function only needs the file to be removed, and doesn't save changes or
   * update the user list like removeTab does.
   * @param {Object} store vuex store
   * @param {string} tabPath the path to the tab that needs to be removed
   */
  removeTabByPath (store, tabPath) {
    if (tabPath === store.state.openFile) {
      if (store.state.tabs.length === 1) {
        store.commit('updateOpenFile', '')
        store.dispatch('updatePieceTable', create(''))
      } else {
        let i = 0
        for (let tab of store.state.tabs) {
          if (tab.filePath === tabPath) {
            break
          }
          i++
        }
        store.dispatch('prevTab', i)
      }
    }
    store.commit('removeTab', tabPath)
  },
  updateCodeAction (state, newCode) {
    state.commit('updateCode', newCode)
  },
  /**
   * Sends a request for a lock to the server.
   * @param {} state
   * @param {start: {id, offset}, end: {id, offset}} payload
   */
  requestLockAction (state, payload) {
    connector.request('file-lock-request', 'file-lock-response',
      {
        'file_path': state.openFile,
        'piece_uuid': payload.start.id,
        'offset': payload.start.offset,
        'length': lengthBetween(this.state.pieces, payload.start.id,
          payload.start.offset, payload.end.start, payload.end.offset)
      }
    )
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
   * @param {int} direction 1 for moving to the next tab, 0 for to the previous
   */
  scrollTab (store, direction) {
    let i = 0
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
