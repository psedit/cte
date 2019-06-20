<template>
  <div class="editor">
    <div class="editor-pieces">
      <editor-piece
              v-for="(piece, index) in pieces"
              v-if="piece.text.length > 0"
              :key="piece.pieceID"
              :index="index"
              :pieces="pieces"
              :dragStart="lockDragStartLocation"
              :dragEnd="lockDragEndLocation"
              @lockDragStart="lockDragStart"
              @lockDragUpdate="lockDragUpdate"
              @lockDragEnd="lockDragEnd"
              @mounted="editorMount"
              ref="editorPieces"
      />
    </div>

    <ghost-cursors />
    <!--<div id="placeholder" v-if="!this.ready">⇚ Select a file</div>-->
    <div class="user-list">
      <div class="user-list-item" v-for="user in activeUsers" :title="user.username" :style="userStyle(user)">{{ user.username[0].toUpperCase() }}</div>
    </div>
  </div>
</template>

<script>
  import EditorPiece from './Editor/EditorPiece'
  import {getRandomColor} from './Editor/RandomColor'
  import connector from '../../main/connector'
  import { convertChangeToJS, edit, rangeToAnchoredLength } from '../../main/pieceTable'
  import GhostCursors from './Editor/GhostCursors'

  export default {
    name: 'Editor',

    components: {
      GhostCursors,
      EditorPiece
    },
    data () {
      return {
        code: '',
        activeUsers: [],
        lockDragStartLocation: null,
        lockDragEndLocation: null,
        dragList: null
      }
    },
    methods: {
      editorMount (editorPiece) {
        const index = this.$refs.editorPieces.indexOf(editorPiece)
        this.initializeEditor(index)
        if (index === this.pieces.length - 1) {
          // this.initalizeEditors()
        }
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

      /** Updates the code that is viewed by the editor. */
      updateUsers (cursors) {
        this.activeUsers = cursors.map(cursor => {
          return {
            username: cursor.username,
            line: cursor.line,
            ch: cursor.ch,
            color: getRandomColor(cursor.username)
          }
        })
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
      userStyle (user) {
        return {
          backgroundColor: user.color
        }
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
      pieces () {
        return this.$store.state.fileTracker.pieces
      },
      pieceTable () {
        return this.$store.state.fileTracker.pieceTable
      },
      filePath () {
        return this.$store.state.fileTracker.openFile
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
      addEventListener('mouseup', (e) => {
        if (!e.composedPath()[0].classList.contains('user-gutter')) {
          this.lockDragCancel()
        }
      })

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
    }
  }
</script>

<style scoped lang="scss">
  .editor{
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

  #placeholder{
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
      display: inline-block;
      width: 2em;
      height: 2em;
      border-radius: 1em;
      margin-left: 0.5em;
      line-height: 2em;
      text-align: center;
      background: black;
      color: #fff;
      cursor: pointer;
    }
  }
</style>
