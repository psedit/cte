<template>
  <div class="codemirror-wrapper" ref="wrapper"></div>
</template>

<script>
  import CodeMirror from 'codemirror/lib/codemirror'
  import 'codemirror/lib/codemirror.css'
  import 'codemirror/theme/cobalt.css'
  import 'codemirror/mode/javascript/javascript'

  import Vue from 'vue'
  import GhostCursors from './GhostCursors'

  import Connector from '../../../main/connector'
  // import 'codemirror/keymap/vim'

  export default {
    name: 'CodeMirror',

    data () {
      return {
        codemirror: null,
        cminstance: null,
        options: {
          // keyMap: 'vim',
          mode: 'javascript',
          // lineSeparator: '\n',
          lineNumbers: true,
          theme: 'cobalt',
          smartIndent: true,
          lineWrapping: true,
          showCursorWhenSelecting: true,
          gutters: ['locker', 'CodeMirror-linenumbers']
        },
        ghostCursors: null
      }
    },

    props: {
      value: String
    },

    watch: {
      value (newVal, oldVal) { // watch it
        this.cminstance.setValue(this.value)
        // console.log('Prop changed: ', newVal, ' | was: ', oldVal)
      }
    },

    methods: {
      initialize () {
        this.codemirror = CodeMirror(this.$refs.wrapper, this.options)
        this.cminstance = this.codemirror
        this.cminstance.setValue(this.value)

        // add ghost cursor
        this.initializeGhostCursors()

        this.$emit('ready', this.codemirror)

        // setup event handlers
        this.codemirror.on('gutterClick', (cm, line) => {
          const info = cm.lineInfo(line)
          // console.log(info.wrapClass)
          if (info.wrapClass === 'lock') {
            this.unlock(line, line)
          } else {
            this.lock(line, line)
          }
        })

        /* Decide whether to keep changes. */
        this.codemirror.on('beforeChange', (cm, change) => {
          // console.log(change)
          const line = change.to.line
          const info = cm.lineInfo(line)
          /* Cancel change if it was initiated by a user outside of their
           * locked sections */
          if (change.origin !== 'setValue' && info.wrapClass !== 'lock') {
            change.cancel()
          }
        })

        this.codemirror.on('cursorActivity', (cm) => {
          const cursorPos = cm.doc.getCursor()
          Connector.send('cursor-move', {
            file_path: this.$store.state.fileTracker.openFile,
            row: cursorPos.line,
            column: cursorPos.ch
          })
        })

        // prevents funky dynamic rendering
        this.refresh()
      },

      initializeGhostCursors () {
        // debugger
        const wrapper = this.cminstance.display.cursorDiv.parentElement
        const GhostCursorClass = Vue.extend(GhostCursors)
        this.ghostCursors = new GhostCursorClass({
          propsData: {
            cminstance: this.cminstance
          }
        })

        this.ghostCursors.$mount()
        wrapper.appendChild(this.ghostCursors.$el)
      },

      lock (start, end) {
        for (let line = start; line <= end; line++) {
          if (this.cminstance.wrapClass !== 'lock') {
            this.cminstance.addLineClass(line, 'wrap', 'lock')
          }
        }
      },

      unlock (start, end) {
        for (let line = start; line <= end; line++) {
          if (this.cminstance.wrapClass === 'lock') {
            this.cminstance.removeLineClass(line, 'wrap', 'lock')
          }
        }
      },

      refresh () {
        this.$nextTick(() => {
          this.cminstance.refresh()
        })
      },

      destroy () {
        // garbage cleanup
        const element = this.cminstance.doc.cm.getWrapperElement()
        element && element.remove && element.remove()
      }
    },

    mounted () {
      window.CodeMirror = CodeMirror
      this.initialize()
      window.edit = this.cminstance
    },

    beforeDestroy () {
      this.destroy()
    }
  }
</script>

<style lang="scss">

  .codemirror-wrapper, .CodeMirror{
    height: 100%;
  }

  @keyframes blinker {
    to {
      opacity: 0;
    }
  }

  .lock {
    background-color: rgba(#600, .5);

    .CodeMirror-gutter-wrapper {
      &:before {
      }

    }
  }
</style>
