<template>
  <div class="ghost-cursors">
    <ghost-cursor v-for="(cursor, index) in cursors"
                 :filepath="cursor.filepath"
                 :username="cursor.username"
                 :line="cursor.line"
                 :ch="cursor.ch"
                 :cminstance="cm"
                 :key="index"
    />
  </div>
</template>

<script>
  import GhostCursor from './GhostCursor'
  import Connector from '../../../main/connector'

  export default {
    name: 'GhostCursors',

    components: {
      GhostCursor
    },

    props: [],

    data () {
      return {
        cursors: [],
        piece: null,
        cm: null
      }
    },
    mounted () {
      this.initializeListeners()
      // Connector.addEventListener('open', this.initializeListeners)
    },

    methods: {
      init (cm, piece) {
        console.log(cm, piece)
        this.piece = piece
        this.cm = cm
      },
      initializeListeners () {
        Connector.listenToMsg('cursor-move-broadcast', ({content}) => {
          if (content.piece_id !== this.piece.pieceID) return
          console.log(content)
          this.moveCursor(content.username, content.file_path, content.piece_id, content.offset, content.column)
        })

        this.$store.subscribeAction({
          after: (action, state) => {
            if (action.type !== 'openFile') return

            console.log(action, state)
            this.changeFilepath(action.payload)
          }
        })
      },

      addCursor (username, filepath, pieceID, line, ch) {
        if (pieceID !== this.piece.pieceID) return
        debugger
        this.cursors.push({username, filepath, pieceID, line, ch})
      },

      moveCursor (username, filepath, pieceID, row, column) {
        if (pieceID !== this.piece.pieceID) return
        for (let i = 0; i < this.cursors.length; i++) {
          if (this.cursors[i].username === username) {
            this.cursors[i].filepath = filepath
            this.cursors[i].pieceID = pieceID
            this.cursors[i].ch = column
            this.cursors[i].line = row
            console.log(username, column, row)
            return
          }
        }
        this.addCursor(username, filepath, pieceID, row, column)
      },
      // updateOpenFile
      changeFilepath (path) {
        this.cursors.splice(0, this.cursors.length)
        return Connector.request(
          'cursor-list-request',
          'cursor-list-response',
          { file_path: path }
        ).then((response) => {
          for (const cursor of response.cursor_list) {
            this.addCursor(
              cursor[0],
              path,
              cursor[1],
              cursor[2],
              cursor[3]
            )
          }
        })
      }
    }
  }
</script>

<style scoped>
  .ghost-cursors {
    position: absolute;
    top: 0;
    z-index: 4;
  }
</style>
