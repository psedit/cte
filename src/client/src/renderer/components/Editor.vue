<template>
  <div class="editor">
    <theme-switch @theme-change="themeChange"/>
    <div class="editor-pieces">
      <transition-group name="swap" tag="div">
        <editor-piece 
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
  import EditorPiece from './Editor/EditorPiece'
  import ThemeSwitch from './ThemeSwitch'
  import convert from './Editor/cursor'
  import connector from '../../main/connector'
  import { getRandomColor } from './Editor/RandomColor'
  import { convertChangeToJS, edit, rangeToAnchoredLength } from '../../main/pieceTable'

  export default {
    name: 'Editor',
    components: {
      EditorPiece,
      ThemeSwitch
    },
    data () {
      return {
        lockDragStartLocation: null,
        lockDragEndLocation: null,
        dragList: null,
        lightTheme: false
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
            console.log(cursorList)
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
      }
    },
    methods: {
      editorUpdate () {},
      editorViewPortChange (index) {
        setTimeout(() => {
          this.$refs.editorPieces.forEach(piece => {
            if (!piece) return
            piece.updateLineNumbers()
          })
        }, 10)
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
      removeDragMarkers () {
        for (let key in this.components) {
          this.components[key].$options.cminstance.clearGutter('user-gutter')
        }
      },
      requestLock (startId, startOffset, endId, endOffset) {
        let payload = { start: {id: startId, offset: startOffset},
          end: {id: endId, offset: endOffset}}
        this.$store.dispatch('requestLock', payload)
      },
      lockDragStart (line, index) {
        // console.log('start', line, index)
        this.lockDragStartLocation = {piece: index, line}
        this.lockDragEndLocation = {piece: index, line}
      },
      lockDragUpdate (line, index) {
        if (this.lockDragStartLocation) {
          this.lockDragEndLocation = {piece: index, line}
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
        console.log('cancel')
        this.lockDragStartLocation = null
        this.lockDragEndLocation = null
        for (let key in this.components) {
          this.components[key].$options.cminstance.clearGutter('user-gutter')
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
      }
    },
    mounted () {
      connector.addEventListener('open', () => {
        connector.listenToMsg('file-delta-broadcast', ({ content }) => {
          if (content.file_path === this.filePath) {
            const newPieceTable = edit(this.pieceTable, content.piece_uuid, content.content.split('\n').map(val => val + '\n'))
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
.swap-enter-to {
  opacity: 1;
  max-height: 10000px;
  margin-bottom: 0px;
  // display: block;
}

.swap-enter {
  opacity: 0;
  max-height: 0px;
  margin-bottom: -1px;
}

.swap-enter-active {
  // display: none;
  // transition: opacity 1s 5s;
  transition: all 0s 0.35s;
}

.swap-leave-active {
  // transition: opacity 0s 0.5s;
  transition: opacity 0s 0.35s;
}

.swap-leave-to {
  opacity: 0;
}

.editor {
  width: 100%;
  overflow-y: hidden;
  background-color: #272822;
}

.editor-pieces {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
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
