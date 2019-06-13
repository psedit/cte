<template>
  <div id="ghost-cursors">
    <ghost-cursor v-for="cursor in cursors"
                 :filepath="cursor.filepath"
                 :username="cursor.username"
                 :line="cursor.line"
                 :ch="cursor.ch"
                 :cminstance="cminstance"
                 :key="cursor.filepath + cursor.username"/>
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
        cursors: []
      }
    },
    mounted () {
      Connector.addEventListener('open', this.initializeListeners)
    },

    methods: {
      initializeListeners () {
        Connector.listenToMsg('cursor-move-broadcast', ({content}) => {
          this.moveCursor(content.username, content.file_path, content.row, content.column)
        })
      },

      addCursor (username, filepath, line, ch) {
        this.cursors.push({username, filepath, line, ch})
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
      },

      changeFilepath (path) {
        this.cursors.splice(0, this.cursors.length)
        Connector.request(
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
        })
      }
    }
  }
</script>

<style scoped>

</style>
