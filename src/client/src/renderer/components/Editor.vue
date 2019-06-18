<template>
  <div class="editor">
    <code-mirror v-show="this.ready" v-model="code" ref="codemirror"/>

    <div id="placeholder" v-if="!this.ready">⇚ Select a file</div>
    <div class="user-list">
      <div class="user-list-item" v-for="user in activeUsers" :title="user.username" :style="userStyle(user)">{{ user.username[0].toUpperCase() }}</div>
    </div>
  </div>
</template>

<script>
  import CodeMirror from './Editor/CodeMirror'
  import connector from '../../main/connector.js'
  import {getRandomColor} from './Editor/RandomColor'

  export default {
    name: 'Editor',

    components: {
      CodeMirror
    },
    data () {
      return {
        code: '',
        activeUsers: []
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
      userStyle (user) {
        return {
          backgroundColor: user.color
        }
      }

    },

    computed: {
      ready () {
        return this.code !== undefined && this.code !== ''
      }
    },

    mounted () {
      // this.socket_init()

      // Add fake demo cursor
      const cm = this.$refs.codemirror

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
      height: calc(100vh - 2em);
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
