<template>
  <div class="editor" :class="{lightTheme}" ref="mainEditor" @scroll="handleScroll">
    <theme-switch @theme-change="themeChange"/>
    <add-piece-button class="add-piece-button-top"/>
    <div class="editor-pieces" ref="editorPiecesList">
      <transition-group name="swap" tag="editorPieceGroup">
        <editor-piece class="editor-piece"
          v-for="(piece, index) in pieces"
          v-if="piece.text.length > 0"
          :key="piece.pieceID + piece.username"
          :index="index"
          :theme="lightTheme"
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
  /**
   * @vue-prop {String} pizza
   */
  import Vue from 'vue'
  import EditorPiece from './Editor/EditorPiece'
  import ThemeSwitch from './ThemeSwitch'
  import convert from './Editor/cursor'
  import connector from '../../main/connector'
  import { getRandomColor } from './Editor/RandomColor'
  import { convertChangeToJS, edit, rangeToAnchoredLength } from '../../main/pieceTable'
  import AddPieceButton from './Editor/AddPieceButton'

  export default {
    name: 'Editor',
    components: {
      EditorPiece,
      ThemeSwitch,
      AddPieceButton
    },
    /**
     *
     * @returns {{dragList: null, lockDragStartLocation: null, lockDragEndLocation: null}}
     */
    data () {
      return {
        lockDragStartLocation: null,
        lockDragEndLocation: null,
        dragList: null,
        lightTheme: false,
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
        Vue.nextTick(this.restoreEditorScroll)
      },
      pieceTable: function (newTable, oldTable) {
        Vue.nextTick(this.restoreEditorScroll)
      },
      scrollHeight: function () {
        this.$nextTick(this.restoreEditorScroll)
      }
    },
    methods: {
      handleScroll () {
        this.restoreScrollY = this.$refs.mainEditor.scrollTop
      },
      editorUpdate () {
        this.$nextTick(this.restoreEditorScroll)
      },
      editorViewPortChange (index) {
        setTimeout(() => {
          this.$refs.editorPieces.forEach(piece => {
            if (!piece) return
            piece.updateLineNumbers()
          })
          // this.restoreEditorScroll()
        }, 10)
        // this.$nextTick(self.restoreEditorScroll)
      },
      themeChange (lightTheme) {
        console.log('Changing theme')
        this.lightTheme = lightTheme
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
      restoreEditorScroll () {
        const editorElement = this.$refs.mainEditor
        if (editorElement.scrollHeight - editorElement.clientHeight <= this.restoreScrollY) {
          console.log('Current editor too small for restoration.')
          this.restoreScrollY -= 1
          this.$nextTick(this.restoreEditorScroll)
        } else {
          // console.log(Math.min(this.restoreScrollY, editorElement.scrollHeight - editorElement.clientHeight))
          editorElement.scrollTop = Math.min(this.restoreScrollY, editorElement.scrollHeight - editorElement.clientHeight)
        }
      },
      lockDragStart (line, index) {
        this.lockDragStartLocation = {piece: index, line}
        this.lockDragEndLocation = {piece: index, line}
        Vue.nextTick(this.restoreEditorScroll)
      },
      lockDragUpdate (line, index) {
        if (this.lockDragStartLocation !== null) {
          if (this.lockDragStartLocation) {
            this.lockDragEndLocation = {piece: index, line}
          }
          Vue.nextTick(this.restoreEditorScroll)
        }
      },
      lockDragEnd (line, index) {
        if (this.lockDragStartLocation === null) return

        let draggedLock = rangeToAnchoredLength(this.$store.state.fileTracker.pieceTable,
          this.lockDragStartLocation.piece, this.lockDragStartLocation.line,
          this.lockDragEndLocation.piece, this.lockDragEndLocation.line)

        connector.request('file-lock-request', 'file-lock-response', {
          file_path: this.$store.state.fileTracker.openFile,
          piece_uuid: this.pieces[draggedLock.index].pieceID,
          offset: draggedLock.offset,
          length: draggedLock.length
        }).then(response => console.log(response))

        this.lockDragCancel()
      },
      lockDragCancel () {
        if (this.lockDragStartLocation !== null) {
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
        let ext = this.filePath.match(/\.\w+/)
        if (!ext) return null

        ext = ext[0].toLowerCase()
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
          // debugger
          if (content.file_path === this.filePath) {
            const newPieceTable = edit(this.pieceTable, content.piece_uuid, content.content.replace(/\n$/, '').split('\n').map(val => val + '\n'))
            this.$store.dispatch('updatePieceTable', newPieceTable)
          }
        })

        connector.listenToMsg('file-piece-table-change-broadcast', ({ content }) => {
          const { textBlocks } = this.pieceTable
          const update = convertChangeToJS(textBlocks, content)
          if (update.filePath === this.filePath) {
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

.editor {
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  overflow-y: scroll;
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
  overflow-y: visible;
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

.editor {
  width: 100%;
  height: auto;
  overflow-y: scroll;
  background-color: #272822;
  &.lightTheme {
    background-color: #fff;

  }
}

.editor-pieces {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
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
