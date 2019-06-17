<template>
  <div class="editor">
    <div class="editor-pieces">
      <editor-piece
              v-for="(code, index) in pieces"
              :key="index"
              :index="index"
              :pieces="pieces"
              :editable="index === 1"
              @lockDragStart="lockDragStart"
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

  // temp code pieces
  const pieces = [`const a  = 1;
const b = 1;
/*`,
  ` * Calculates fibonacci's sequence
 */
console.log(a)
console.log(b)
while(true){`,
  `    [a, b] = [b, a+b]
    console.log(a)
}`
  ]

  export default {
    name: 'Editor',

    components: {
      EditorPiece
    },
    data () {
      return {
        code: '',
        pieces: pieces,
        activeUsers: [],
        lockDragRange: null
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
        this.lockDragRange = {piece: index, line}
      },
      lockDragEnd (line, index) {
        console.log(this.lockDragRange)
        if (!this.lockDragRange) return

        console.log(`Request lock from ${this.lockDragRange.piece}:${this.lockDragRange.line} to ${index}:${line}`)
      },
      lockDragCancel () {
        // console.log('cancel')
        this.lockDragRange = null
      }
    },

    computed: {
      ready () {
        return this.code !== undefined && this.code !== ''
      }
    },

    mounted () {
      const cm = this.$refs.codemirror

      this.updateCode()
      this.$store.subscribe((mutation, state) => {
        if (mutation.type === 'updateCode') {
          this.updateCode()
          cm.ghostCursors.changeFilepath(this.$store.state.fileTracker.openFile).then(cursors => {
            console.log(cursors)
            this.updateUsers(cursors)
          })
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
      height: calc(100vh - 2em);
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
