<template>
  <div class="editor">
    <div class="editor-pieces">
      <editor-piece
              v-for="(piece, index) in pieces"
              :key="piece.pieceID"
              :index="index"
              :pieces="pieces"
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
        lockDragEndLocation: null
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
      },
      lockDragStart (line, index) {
        // console.log('start', line, index)
        this.lockDragStartLocation = {piece: index, line}
      },
      lockDragUpdate (line, index) {
        if (this.lockDragStart) {
          this.lockDragEndLocation = {piece: index, line}
          this.updateDrag()
        }
      },
      lockDragEnd (line, index) {
        console.log(this.lockDragStartLocation)
        if (!this.lockDragStartLocation) return

        console.log(`Request lock from ${this.lockDragStartLocation.piece}:${this.lockDragStartLocation.line} to ${index}:${line}`)
        this.lockDragStartLocation = null
        this.lockDragEndLocation = null
        for (var key in this.components) {
          this.components[key].$options.cminstance.clearGutter('user-gutter')
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
