/* globals expect describe it */
import store from '../../../src/renderer/store/modules/fileTracker'
import Tab from '../../../src/renderer/components/Tabs/tabType'

describe('fileTracker', () => {
  const { mutations } = store

  describe('mutations', () => {
    const { addTab, removeTab, renameTab } = mutations
    const filePath = 'randomFilePath'
    const randomTab = new Tab(filePath)
    describe('addTab', () => {
      it('should add a tab to the list of tabs', () => {
        const state = {
          tabs: []
        }
        addTab(state, filePath)
        expect(state.tabs).to.deep.equal([randomTab])
      })

      it('should not add a tab to the list of tabs that already contains that filepath', () => {
        const state = {
          tabs: [randomTab]
        }
        addTab(state, filePath)
        expect(state.tabs).to.deep.equal([randomTab])
      })
    })

    describe('removeTab', () => {
      it('should remove the tab passed from the tab state', () => {
        const state = {
          tabs: [randomTab]
        }
        removeTab(state, filePath)
        expect(state.tabs).to.deep.equal([])
      })
    })

    describe('removeTab', () => {
      it('should remove the tab passed from the tab state', () => {
        const state = {
          tabs: [randomTab]
        }
        removeTab(state, '')
        expect(state.tabs).to.deep.equal([randomTab])
      })
    })

    describe('renameTab', () => {
      it('should rename the filepath to the passed filepath', () => {
        const state = {
          openFile: filePath,
          tabs: [randomTab]
        }
        const randomNewPath = 'randomNewPath'
        const payload = {
          pathToDir: '',
          oldName: filePath,
          newName: randomNewPath
        }
        renameTab(state, payload)
        expect(state.openFile).to.deep.equal(randomNewPath)
        expect(state.tabs).to.deep.equal([new Tab(randomNewPath)])
      })
    })
  })

  describe('actions', () => {

  })
})

