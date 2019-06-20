<template>
  <div class="editor">
    <div class="editor-pieces">
      <editor-piece
              v-for="(piece, index) in pieces"
              v-if="piece.text.length > 0"
              :key="piece.pieceID"
              :index="index"
              :pieces="pieces"
              @lockDragStart="lockDragStart"
              @lockDragEnd="lockDragEnd"
              @mounted="editorMount"
              ref="editorPieces"
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
  import {convertChangeToJS, edit} from '../../main/pieceTable'
  // import Vue from 'vue'

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
        lockDragRange: null
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
      userStyle (user) {
        return {
          backgroundColor: user.color
        }
      },
      lockDragStart (line, index) {
        // console.log('start', line, index)
        this.lockDragRange = {piece: index, line}
      },
      lockDragEnd (line, index) {
        console.log(this.lockDragRange)
        if (!this.lockDragRange) return

        console.log(`Request lock from ${this.lockDragRange.piece}:${this.lockDragRange.line} to ${index}:${line}`)

        if (this.lockDragRange.piece !== index) alert('NOT SUPPORTED')

        connector.request('file-lock-request', 'file-lock-response', {
          file_path: this.$store.state.fileTracker.openFile,
          piece_uuid: this.pieces[this.lockDragRange.piece].pieceID,
          offset: Math.min(this.lockDragRange.line, line),
          length: Math.abs(this.lockDragRange.line - line) + 1
        }).then(response => console.log(response))
      },
      lockDragCancel () {
        this.lockDragRange = null
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
      this.updateCode()
      this.$store.subscribe((mutation, state) => {
        if (mutation.type === 'updateCode') {
          this.updateCode()
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
