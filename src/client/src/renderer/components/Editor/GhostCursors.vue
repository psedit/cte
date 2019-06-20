<template>
  <div id="ghost-cursors">
    <ghost-cursor v-for="(cursor, index) in cursors"
                 :filepath="cursor.filepath"
                 :username="cursor.username"
                 :piece_id="cursor.pieceID"
                 :line="cursor.line"
                 :ch="cursor.ch"
                 :cminstance="cminstance"
                 :key="index"/>
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

    props: ['cminstance'],

    data () {
      return {
        cursors: {}
      }
    },
    mounted () {
      this.initializeListeners()
      // Connector.addEventListener('open', this.initializeListeners)
    },

    methods: {
      initializeListeners () {
        Connector.listenToMsg('cursor-move-broadcast', ({content}) => {
          console.log(content)
          this.moveCursor(content.username, content.file_path, content.row, content.column)
        })
      },

      addCursor (username, filepath, pieceID, line, ch) {
        this.cursors.push({username, filepath, pieceID, line, ch})
      },

      moveCursor (username, filepath, row, column) {
        for (let i = 0; i < this.cursors.length; i++) {
          if (this.cursors[i].username === username) {
            this.cursors[i].filepath = filepath
            this.cursors[i].ch = column
            this.cursors[i].line = row
            return
          }
        }
        this.addCursor(username, filepath, row, column)
      },

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
              cursor[2]
            )
          }
          return this.cursors
        })
      }
    }
  }
</script>

<style scoped>
  #ghost-cursors {
    position: absolute;
    top: 0;
    z-index: 4;
  }
</style>
