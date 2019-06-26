<template>
  <div class="editor" ref="mainEditor" @scroll="handleScroll">
    <add-piece-button class="add-piece-button-top"/>
    <div class="editor-pieces" ref="editorPiecesList">
      <transition-group name="swap" tag="editorPieceGroup">
        <editor-piece class="editor-piece"
          v-for="(piece, index) in pieces"
          v-if="piece.text.length > 0"
          :key="piece.pieceID + piece.username"
          :index="index"
          :pieces="pieces"
          :dragStart="lockDragStartLocation"
          :dragEnd="lockDragEndLocation"
          @lockDragStart="lockDragStart"
          @lockDragUpdate="lockDragUpdate"
          @lockDragEnd="lockDragEnd"
          @mounted="editorMount"
          @update="editorUpdate"
          @viewportChange="editorViewPortChange"
          ref="editorPieces"
        />
      </transition-group>
    </div>
    <!--<div id="placeholder" v-if="!this.ready">⇚ Select a file</div>-->
    <div class="user-list" v-if="pieces.length > 0">
      <div
        class="user-list-item"
        v-for="cursor in cursors"
        :key="cursor.username"
        :title="cursor.username"
        :style="{borderColor: cursor.color}"
      >{{ cursor.username.toUpperCase() }}</div>
    </div>
  </div>
</template>

<script>
  import Vue from 'vue'
  import EditorPiece from './Editor/EditorPiece'
  import convert from './Editor/cursor'
  import connector from '../../main/connector'
  import { getRandomColor } from './Editor/RandomColor'
  import { convertChangeToJS, edit, rangeToAnchoredLength } from '../../main/pieceTable'
  import AddPieceButton from './Editor/AddPieceButton'

  export default {
    name: 'Editor',
    components: {
      AddPieceButton,
      EditorPiece
    },
    data () {
      return {
        lockDragStartLocation: null,
        lockDragEndLocation: null,
        dragList: null,
        restoreScrollY: 0
      }
    },
    watch: {
      filePath (val) {
        this.$store.commit('emptyCursors')
        if (val === '') return

        connector.request(
          'cursor-list-request',
          'cursor-list-response',
          { file_path: val }
        ).then(({cursor_list: cursorList}) => {
          for (const [username, pieceID, line, ch] of cursorList) {
            this.$store.commit('addCursor', {
              username,
              pieceID,
              line,
              ch,
              filepath: val,
              color: getRandomColor(username)
            })
          }
        })
      },
      pieces: function (newPieces, oldPieces) {
        console.log('length', newPieces.length)
        this.saveEditorScroll()
        Vue.nextTick(this.restoreEditorScroll)
      },
      pieceTable: function (newTable, oldTable) {
        this.saveEditorScroll()
        Vue.nextTick(this.restoreEditorScroll)
      },
      scrollHeight: function () {
        this.saveEditorScroll()
        this.$nextTick(this.restoreEditorScroll)
      }
    },
    methods: {
      handleScroll () {
        console.log(`scrolled to ${this.$refs.mainEditor.scrollTop}`)
        this.restoreScrollY = this.$refs.mainEditor.scrollTop
      },
      editorUpdate () {
        this.$nextTick(this.restoreEditorScroll)
      },
      editorViewPortChange (index) {
        // this.saveEditorScroll()
        setTimeout(() => {
          this.$refs.editorPieces.forEach(piece => {
            if (!piece) return
            piece.updateLineNumbers()
          })
          // this.restoreEditorScroll()
        }, 10)
        // this.$nextTick(self.restoreEditorScroll)
      },
      editorMount (editorPiece) {
        const index = this.$refs.editorPieces.indexOf(editorPiece)
        this.initializeEditor(index)
      },

      async initializeEditor (index) {
        const piece = this.$refs.editorPieces[index]
        piece.lang = this.lang
        if (index === 0) {
          return piece.initializeEditor()
        }
        piece.$options.startState = await this.getPreviousState(index)
        return piece.initializeEditor()
      },
      async getPreviousState (index) {
        if (index === 0) return undefined
        const prevPiece = this.$refs.editorPieces[index - 1]
        let cm = prevPiece.$options.cminstance
        if (!cm) {
          cm = await this.initializeEditor(index - 1)
        }
        return cm.getStateAfter(cm.lastLine(), true)
      },
      requestLock (startId, startOffset, endId, endOffset) {
        let payload = { start: {id: startId, offset: startOffset},
          end: {id: endId, offset: endOffset}}
        this.$store.dispatch('requestLock', payload)
      },
      saveEditorScroll () {
        console.groupCollapsed('saveEditorScroll')
        console.trace()
        const editorElement = this.$refs.mainEditor
        // this.restoreScrollY = editorElement.scrollTop
        console.log('Saved scroll: ', editorElement.scrollTop)
        console.groupEnd()
      },
      restoreEditorScroll () {
        console.groupCollapsed('restoreEditorScroll')
        console.trace()
        const editorElement = this.$refs.mainEditor
        if (editorElement.scrollHeight - editorElement.clientHeight <= this.restoreScrollY) {
          console.log('Current editor too small for restoration.')
          this.restoreScrollY -= 1
          this.$nextTick(this.restoreEditorScroll)
        } else {
          // console.log(Math.min(this.restoreScrollY, editorElement.scrollHeight - editorElement.clientHeight))
          console.log(`Reset scroll from ${editorElement.scrollTop} to ${this.restoreScrollY} out of ${editorElement.scrollHeight - editorElement.clientHeight}`)
          editorElement.scrollTop = Math.min(this.restoreScrollY, editorElement.scrollHeight - editorElement.clientHeight)
        }
        console.groupEnd()
      },
      lockDragStart (line, index) {
        this.saveEditorScroll()
        this.lockDragStartLocation = {piece: index, line}
        this.lockDragEndLocation = {piece: index, line}
        Vue.nextTick(this.restoreEditorScroll)
      },
      lockDragUpdate (line, index) {
        if (this.lockDragStartLocation !== null) {
          this.saveEditorScroll()
          if (this.lockDragStartLocation) {
            this.lockDragEndLocation = {piece: index, line}
          }
          Vue.nextTick(this.restoreEditorScroll)
        }
      },
      lockDragEnd (line, index) {
        if (this.lockDragStartLocation === null) return

        console.log(`Request lock from ${this.lockDragStartLocation.piece}:${this.lockDragStartLocation.line} to ${index}:${line}`)

        let draggedLock = rangeToAnchoredLength(this.$store.state.fileTracker.pieceTable,
          this.lockDragStartLocation.piece, this.lockDragStartLocation.line,
          this.lockDragEndLocation.piece, this.lockDragEndLocation.line)

        console.log(`PieceIdx: ${draggedLock.index}, Offset: ${draggedLock.offset}, Length: ${draggedLock.length}`)

        connector.request('file-lock-request', 'file-lock-response', {
          file_path: this.$store.state.fileTracker.openFile,
          piece_uuid: this.pieces[draggedLock.index].pieceID,
          offset: draggedLock.offset,
          length: draggedLock.length
        }).then(response => console.log(response))

        this.lockDragCancel()
      },
      showPieceLengths () {
        const table = this.$store.state.fileTracker.pieceTable
        for (let i = 0; i < table.table.length; i++) {
          console.log(`piece ${i} has length ${table.table[i].length}`)
        }
      },
      lockDragCancel () {
        if (this.lockDragStartLocation !== null) {
          this.saveEditorScroll()
          console.log('cancel')
          this.lockDragStartLocation = null
          this.lockDragEndLocation = null
          for (let key in this.components) {
            this.components[key].$options.cminstance.clearGutter('user-gutter')
          }
          this.$nextTick(this.restoreEditorScroll)
        }
      }
    },

    computed: {
      ready () {
        return this.code !== undefined && this.code !== ''
      },
      username () {
        return this.$store.state.user.username
      },
      pieces () {
        return this.$store.state.fileTracker.pieces || []
      },
      pieceTable () {
        return this.$store.state.fileTracker.pieceTable
      },
      filePath () {
        return this.$store.state.fileTracker.openFile
      },
      cursors () {
        return this.$store.state.user.cursors.filter(({filepath}) => filepath === this.filePath)
      },
      lang () {
        if (!this.filePath) return null
        const ext = this.filePath.match(/\.\w+/)[0].toLowerCase()
        if (ext === '.py') {
          return 'python'
        } else if (ext === '.js') {
          return 'javascript'
        }
        return null
      },
      scrollHeight () {
        return this.$refs.mainEditor.scrollHeight
      },
      scrollTop () {
        return this.$refs.mainEditor.scrollTop
      }
    },
    mounted () {
      connector.addEventListener('open', () => {
        connector.listenToMsg('file-delta-broadcast', ({ content }) => {
          if (content.file_path === this.filePath) {
            // this.saveEditorScroll()
            const newPieceTable = edit(this.pieceTable, content.piece_uuid, content.content.split('\n').map(val => val + '\n'))
            this.$store.dispatch('updatePieceTable', newPieceTable)
          }
        })

        connector.listenToMsg('file-piece-table-change-broadcast', ({ content }) => {
          const { textBlocks } = this.pieceTable
          const update = convertChangeToJS(textBlocks, content)
          if (update.filePath === this.filePath) {
            // this.saveEditorScroll()
            this.$store.dispatch('updatePieceTable', update.pieceTable)
          }
        })

        connector.listenToMsg('file-join-broadcast', ({content}) => {
          this.$store.dispatch('moveCursor', {...convert(content), ch: -1, line: -1})
        })

        connector.listenToMsg('cursor-move-broadcast', ({content}) => {
          this.$store.dispatch('moveCursor', convert(content))
        })

        connector.listenToMsg('file-leave-broadcast', ({content}) => {
          this.$store.commit('removeCursor', convert(content))
        })
      })

      addEventListener('mouseup', (e) => {
        if (!e.composedPath()[0].classList.contains('user-gutter')) {
          this.lockDragCancel()
        }
      })
    }
  }
</script>

<style scoped lang="scss">
// .swap-enter-to {
//   opacity: 1;
//   max-height: 0px;
//   margin-bottom: 0px;
//   // display: block;
// }

// .swap-enter {
//   opacity: 0;
//   max-height: 0px;
//   margin-bottom: -1px;
// }

// .swap-enter-active {
//   // display: none;
//   // transition: opacity 1s 5s;
//   transition: all 0s 0.35s;
// }

// .swap-leave-active {
//   // transition: opacity 0s 0.5s;
//   transition: opacity 0s 0.35s;
// }

// .swap-leave-to {
//   opacity: 0;
// }

.editor {
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  overflow-y: scroll;
  overflow-x: scroll;
  background-color: #272822;
}

.editor-pieces {
  // display: flex;
  // flex-direction: column;
  height: auto;
  width: auto;
  overflow-y: hidden;
  padding-bottom: 1000px;
}

.editor-piece {
  height: auto;
  overflow-y: hidden;
  transition: all 0s;
  display: block;
  padding: 0;
  margin: 0;
  top: 0;
}

.editorPieceGroup-enter, .editorPieceGroup-leave-to {
  opacity: 0;
  max-height: 0;
  position: absolute;
}

.editorPieceGroup-leave-active {
  position: absolute;
}

#placeholder {
  font-size: 3em;
  height: 100%;
  width: 100%;
  line-height: 100%;
  color: #555;
  text-align: center;

  &:before {
    content: "";
    display: inline-block;
    height: 100%;
    vertical-align: middle;
  }
}

.user-list {
  position: fixed;
  bottom: 1em;
  right: 1em;

  &-item {
    border-style: solid;
    border-width: 0.1em;
    display: inline-block;
    padding: 0.05em 0.5em;
    border-radius: 2em;
    margin-left: 0.5em;
    line-height: 2em;
    text-align: center;
    background: black;
    color: #fff;
    cursor: pointer;
  }
}
</style>
