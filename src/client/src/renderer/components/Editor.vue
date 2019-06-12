<template>
  <div class="editor">
    <code-mirror v-show="this.ready" v-model="code" ref="codemirror"/>

    <div id="placeholder" v-if="!this.ready">
      ⇚ Select a file
    </div>
  </div>
</template>

<script>
  import CodeMirror from './Editor/CodeMirror'
  import connector from '../../main/connector.js'

  export default {
    name: 'Editor',

    components: {
      CodeMirror
    },
    data () {
      return {
        code: ''
      }
    },
    methods: {
      updateCode () {
        // console.log('hey', this.$store.state)
        this.code = this.$store.state.fileTracker.code
      },
      startFakeMovement () {
        const cm = this.$refs.codemirror
        const timeout = (func) => setTimeout(func, 1000)
        function step1 () {
          cm.updateShadowCursorLocation(0, 1, 2)
          timeout(step2)
        }
        function step2 () {
          cm.updateShadowCursorLocation(0, 1, 3)
          timeout(step3)
        }
        function step3 () {
          cm.updateShadowCursorLocation(0, 3, 2)
          timeout(step4)
        }
        function step4 () {
          cm.updateShadowCursorLocation(0, 3, 4)
          timeout(step1)
        }

        setTimeout(step1, 1000)
      },

      socket_init () {
        console.log('fdjsfs')
        connector.addEventListener('open', () => {
          console.log('Hello')

          connector.listenToMsg('file-lock-change-broadcast', (content) => {
            console.log(content)
          })

          connector.request('file-lock-request', 'file-lock-respond', { file_path: 'file.txt', start: 0, length: -1 }).then((content) => {
            console.log(content)
          })
        })
      }

    },

    computed: {
      ready () {
        return this.code !== undefined && this.code !== ''
      }
    },

    mounted () {
      this.socket_init()

      // Add fake demo cursor
      const cm = this.$refs.codemirror
      cm.addShadowCursor(1, 3, 'Martijn')
      cm.addShadowCursor(4, 3, 'Mund')
      cm.addShadowCursor(0, 3, 'Mark')
      cm.addShadowCursor(6, 3, 'HAL_9000')
      this.startFakeMovement()

      this.updateCode()
      this.$store.subscribe((mutation, state) => {
        if (mutation.type === 'updateCode') {
          this.updateCode()
        }
        // console.log(mutation.type)
        // console.log(mutation.payload)
      })
    }
  }
</script>

<style scoped>
  .editor{
      width: 100%;
      height: calc(100vh - 50px);
  }

  #placeholder{
    font-size: 3em;
    height: 100vh;
    width: 100vh;
    line-height: 100vh;
    color: #555;
    text-align: center;
  }
</style>
