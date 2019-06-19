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

  export default {
    name: 'Editor',

    components: {
      EditorPiece
    },
    data () {
      return {
        code: '',
        // pieces: pieces,
        activeUsers: [],
        lockDragStartLocation: null,
        lockDragEndLocation: null,
        dragList: null
      }
    },
    methods: {
      /** Updates the code that is viewed by the editor. */
      updateCode () {
        this.code = this.$store.state.fileTracker.code
      },
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
      updateDrag () {
        // this.removeDragMarkers()
        // let start = this.lockDragStartLocation
        // let end = this.lockDragEndLocation
        // console.log(start, end)
        // // let lastLine = 0
        // if (indexOffsetCompare(this.lockDragStartLocation, this.lockDragEndLocation) > 0) {
        //   start = this.lockDragEndLocation
        //   end = this.lockDragStartLocation
        // }
        // if (start.piece === end.piece) {
        //   lastLine = end.offset
        // }
        // console.log('components', this.components)
        // for (let line = start.offset;
        //   line < Math.max(this.components[start.piece].$options.cminstance.lineCount(), lastLine); line++) {
        //   this.$components[start.piece].$options.cminstance.setGutterMarker(line, 'user-gutter', this.gutterSelectMarker())
        // }
        // for (let i = start.piece + 1; i < end.piece; i++) {
        //   for (let line = 0; line < this.components[i].$options.cminstance.lineCount(); line++) {
        //     this.$components[i].$options.cminstance.setGutterMarker(line, 'user-gutter', this.gutterSelectMarker())
        //   }
        // }
        // if (start.piece !== end.piece) {
        //   for (let line = end.offset;
        //     line < Math.max(this.components[start.piece].$options.cminstance.lineCount(), end.offset); line++) {
        //     this.$components[end.piece].$options.cminstance.setGutterMarker(line, 'user-gutter', this.gutterSelectMarker())
        //   }
        // }
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
      },
      lockDragUpdate (line, index) {
        if (this.lockDragStartLocation) {
          this.lockDragEndLocation = {piece: index, line}
          this.updateDrag()
        }
      },
      lockDragEnd (line, index) {
        if (this.lockDragStartLocation === null) return
        console.log(this.lockDragStartLocation.piece)
        console.log(this.lockDragStartLocation.line)

        console.log(`Request lock from ${this.lockDragStartLocation.piece}:${this.lockDragStartLocation.line} to ${index}:${line}`)
        // this.requestLock(this.lockDragStartLocation, this.lockDragEndLocation)

        // console.log(`Request lock from ${this.lockDragStartLocation.piece}:${this.LockDragStartLocation.line} to ${index}:${line}`)

        // if (this.lockDragRange.piece !== index) alert('NOT SUPPORTED')

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
      }
    },

    mounted () {
      this.updateCode()
      this.$store.subscribe((mutation, state) => {
        if (mutation.type === 'updateCode') {
          this.updateCode()
          // cm.ghostCursors.changeFilepath(this.$store.state.fileTracker.openFile).then(cursors => {
          //   console.log(cursors)
          //   this.updateUsers(cursors)
          // })
        }
      })

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
        console.log(content)
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
