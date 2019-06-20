<template>
  <div class="editor">
    <div class="editor-pieces">
      <editor-piece
        v-for="(piece, index) in pieces"
        :key="piece.pieceID"
        :index="index"
        :pieces="pieces"
        :dragStart="lockDragStartLocation"
        :dragEnd="lockDragEndLocation"
        @lockDragStart="lockDragStart"
        @lockDragUpdate="lockDragUpdate"
        @lockDragEnd="lockDragEnd"
      />
    </div>
    <!--<div id="placeholder" v-if="!this.ready">⇚ Select a file</div>-->
    <div class="user-list" v-if="pieces.length > 0">
      <div
        class="user-list-item"
        v-for="cursor in cursors"
        :title="cursor.username"
        :style="{borderColor: cursor.color}"
      >{{ cursor.username.toUpperCase() }}</div>
    </div>
  </div>
</template>

<script>
  import EditorPiece from './Editor/EditorPiece'
  import {getRandomColor} from './Editor/RandomColor'
  import connector from '../../main/connector'
  import { convertChangeToJS, edit, rangeToAnchoredLength } from '../../main/pieceTable'

  export default {
    name: 'Editor',
    components: {
      EditorPiece
    },
    data () {
      return {
        lockDragStartLocation: null,
        lockDragEndLocation: null,
        dragList: null,
        cursors: []
      }
    },
    watch: {
      filePath () {
        connector.request(
          'cursor-list-request',
          'cursor-list-response',
          { file_path: this.filePath }
        ).then((response) => {
          this.cursors = response.cursor_list.map(x => {
            return this.cursor(x[0], x[1], x[2], x[3])
          })
        })
      }
    },
    methods: {
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
          this.updateDrag()
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
      },
      cursor (username, pieceID, offset, column) {
        return {
          username,
          pieceID,
          offset,
          column,
          color: getRandomColor(username)
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
        return this.$store.state.fileTracker.pieces
      },
      pieceTable () {
        return this.$store.state.fileTracker.pieceTable
      },
      filePath () {
        return this.$store.state.fileTracker.openFile
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
        connector.listenToMsg('cursor-move-broadcast', ({content}) => {
          console.log(this.filePath, content)
          if (content.file_path === this.filePath && content.username !== this.username) {
            this.cursors = [
              ...this.cursors.filter(({username}) => username !== content.username),
              this.cursor(content.username, content.pieceID, content.offset, content.column)]
          }
        })

        connector.listenToMsg('file-leave-broadcast', ({content}) => {
          console.log(content)
          if (content.file_path === this.filePath) {
            this.cursors = this.cursors.filter(({username}) => username !== content.username)
          }
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
