<template>
  <div class="editor" :class="{lightTheme}" ref="mainEditor">
    <theme-switch @theme-change="themeChange"/>
    <add-piece-button class="add-piece-button-top"/>
    <scroll-bar :max="scrollHeight" v-model="scrollPos" ref="scrollbar"/>

    <div class="editor-pieces" ref="editorPiecesList" :style="{transform: `translateY(${-scrollPos}px)`}">
      <transition-group name="swap" tag="editorPieceGroup">
        <editor-piece class="editor-piece"
          v-for="(piece, index) in pieces"
          v-if="piece.text.length > 0"
          :key="piece.pieceID"
          :index="index"
          :theme="lightTheme"
          :pieces="pieces"
          :dragStart="lockDragStartLocation"
          :dragEnd="lockDragEndLocation"
          @lockDragStart="lockDragStart"
          @lockDragUpdate="lockDragUpdate"
          @lockDragEnd="lockDragEnd"
          @mounted="editorMount"
          @viewportChange="editorViewPortChange"
          @update="editorUpdate"
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
  // import Vue from 'vue'
  import EditorPiece from './Editor/EditorPiece'
  import ThemeSwitch from './ThemeSwitch'
  import convert from './Editor/cursor'
  import connector from '../../main/connector'
  import { getRandomColor } from './Editor/RandomColor'
  import { convertChangeToJS, edit, rangeToAnchoredLength } from '../../main/pieceTable'
  import AddPieceButton from './Editor/AddPieceButton'
  import ScrollBar from './Editor/ScrollBar'

  export default {
    name: 'Editor',
    components: {
      EditorPiece,
      ThemeSwitch,
      AddPieceButton,
      ScrollBar
    },
    /**
     * Data properties
     * @returns {{dragList: null, lockDragStartLocation: null, lockDragEndLocation: null}}
     */
    data () {
      return {
        lockDragStartLocation: null,
        lockDragEndLocation: null,
        dragList: null,
        lightTheme: false,
        scrollPos: 0
      }
    },
    watch: {
      /* When filePath changes,
       * handle changing cursors.
       */
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

      scrollPos () {
        if (this.scrollPos < 0) {
          this.scrollPos = 0
        } else if (this.scrollPos > this.$refs.editorPiecesList.clientHeight - 20) {
          this.scrollPos = this.$refs.editorPiecesList.clientHeight - 20
        }
      }
    },
    methods: {
      /* Update the line numbers for each piece.
       */
      editorViewPortChange (index) {
        setTimeout(() => {
          this.$refs.editorPieces.forEach(piece => {
            if (!piece) return
            piece.updateLineNumbers()
          })
        }, 10)
      },
      themeChange (lightTheme) {
        this.lightTheme = lightTheme
      },
      editorMount (editorPiece) {
        const index = this.$refs.editorPieces.indexOf(editorPiece)
        this.initializeEditor(index)
      },
      editorUpdate () {
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
      /* Let the editor piece at index get the state of the previous piece.
       */
      async getPreviousState (index) {
        if (index === 0) return undefined
        const prevPiece = this.$refs.editorPieces[index - 1]
        let cm = prevPiece.$options.cminstance
        if (!cm) {
          cm = await this.initializeEditor(index - 1)
        }
        return cm.getStateAfter(cm.lastLine(), true)
      },
      /* request to lock part of the file.
       */
      requestLock (startId, startOffset, endId, endOffset) {
        let payload = { start: {id: startId, offset: startOffset},
          end: {id: endId, offset: endOffset}}
        this.$store.dispatch('requestLock', payload)
      },
      /* Handles the selection of a locking area.
       */
      lockDragStart (line, index) {
        this.lockDragStartLocation = {piece: index, line}
        this.lockDragEndLocation = {piece: index, line}
      },
      lockDragUpdate (line, index) {
        if (this.lockDragStartLocation !== null) {
          if (this.lockDragStartLocation) {
            this.lockDragEndLocation = {piece: index, line}
          }
        }
      },
      /* Requests lock when region is selected
       */
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
        })

        this.lockDragCancel()
      },
      /* Cancels lock selection.
       */
      lockDragCancel () {
        if (this.lockDragStartLocation) {
          this.lockDragStartLocation = null
          this.lockDragEndLocation = null
          for (let key in this.components) {
            this.components[key].$options.cminstance.clearGutter('user-gutter')
          }
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
        if (!this.$refs.editorPiecesList) return 0
        return this.$refs.editorPiecesList.clientHeight
      }
    },
    mounted () {
      /* Listen to changes in the
       */
      connector.addEventListener('open', () => {
        connector.listenToMsg('file-delta-broadcast', ({ content }) => {
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

      this.$refs.editorPiecesList.style.top = 0

      this.$el.addEventListener('wheel', event => {
        this.scrollPos = this.scrollPos + event.deltaY * 0.2
        this.scrollPos = Math.max(0, this.scrollPos)
        this.scrollPos = Math.min(this.$refs.editorPiecesList.clientHeight - 20, this.scrollPos)
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

[v-cloak] {
  display: none;
}

.editor {
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  overflow-y: hidden;
  background-color: #272822;
  &.lightTheme {
    background-color: #fff;

  }
}

.editor-pieces {
  // display: flex;
  // flex-direction: column;
  // height: 1000000pt;
  position: relative;
  width: auto;
  overflow-y: visible;
  transition: transform linear 100ms;
  // padding-bottom: 1000px;
  // min-height: 1000000pt;
}

.editor-piece {
  height: auto;
  overflow-y: visible;
  display: block;
  padding: 0;
  margin: 0;
  top: 0;
  opacity: 1;
}

.editorPieceGroup {
  min-height: 100%
}

.swap-enter-active {
  /*position: float;*/
  opacity: 1;
  // max-height: 0;
  // display: block;
  transition: all 1s;
}

.swap-leave-active {
  position: relative;
  opacity: 1;
  transition: all 1s;
  // max-height: 0;
  display: none;
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
