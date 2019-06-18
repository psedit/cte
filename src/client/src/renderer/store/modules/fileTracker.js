import Tab from '../../components/Tabs/tabType'
import connector from '../../../main/connector'
import { convertToJS, getFile, lengthBetween } from '../../../main/pieceTable'

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
   * @param {FilePiece} pieces
   */
  updatePieces (state, pieces) {
    state.pieces = pieces
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
      const pieces = getFile(pieceTable)
      store.commit('updatePieceTable', pieceTable)
      store.commit('updatePieces', pieces)

      // fs.writeFile(filePath, data.file_content, (err) => {
      //   if (err) console.error(err)
      // })
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
        store.dispatch('openFile', store.state.tabs[(i + 1) % store.state.tabs.length].filePath)
      }
    }
    store.commit('removeTab', tabToRemove)
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
    console.log('request Lock of length', lengthBetween(this.state.pieces, payload.start.id,
      payload.start.offset, payload.end.start, payload.end.offset))
    connector.request('file-lock-request', 'file-lock-response',
      {
        'file_path': state.openFile,
        'piece_uuid': payload.start.id,
        'offset': payload.start.offset,
        'length': lengthBetween(this.state.pieces, payload.start.id,
          payload.start.offset, payload.end.start, payload.end.offset)
      }
    )
  }
}

export default {
  state,
  mutations,
  actions
}
