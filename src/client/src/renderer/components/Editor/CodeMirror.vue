<template>
    <div class="codemirror-wrapper" ref="wrapper"></div>
</template>

<script>
  import CodeMirror from 'codemirror/lib/codemirror'
  import 'codemirror/lib/codemirror.css'
  import 'codemirror/theme/cobalt.css'
  import 'codemirror/mode/javascript/javascript'

  export default {
    name: 'CodeMirror',

    data () {
      return {
        codemirror: null,
        cminstance: null,
        options: {
          mode: 'javascript',
          lineSeparator: '\n',
          lineNumbers: true,
          theme: 'cobalt',
          smartIndent: true,
          lineWrapping: true,
          showCursorWhenSelecting: true,
          gutters: ['locker', 'CodeMirror-linenumbers']
        },
        // shadowCursors: [
        //   {char: 5, line: 1},
        //   {char: 3, line: 3}
        // ],
        ghostCursorWrapper: null,
        ghostCursors: []
      }
    },

    props: {
      value: String
    },

    methods: {
      initialize () {
        this.codemirror = CodeMirror(this.$refs.wrapper, this.options)
        this.cminstance = this.codemirror
        this.cminstance.setValue(this.value)

        // add ghost cursor
        const wrapper = this.cminstance.display.wrapper
        const cursorsWrapper = document.createElement('div')
        cursorsWrapper.classList.add('shadowCursors')
        wrapper.appendChild(cursorsWrapper)
        this.ghostCursorWrapper = cursorsWrapper

        this.$emit('ready', this.codemirror)

        // setup event handlers
        this.codemirror.on('gutterClick', (cm, line) => {
          const info = cm.lineInfo(line)
          console.log(info.wrapClass)
          if (info.wrapClass === 'lock') {
            this.unlock(line, line)
          } else {
            this.lock(line, line)
          }
        })

        this.codemirror.on('beforeChange', (cm, change) => {
          console.log(change)
          const line = change.to.line
          const info = cm.lineInfo(line)
          if (info.wrapClass === 'lock') {
            change.cancel()
          }
        })

        // prevents funky dynamic rendering
        this.refresh()
      },

      addShadowCursor (line, ch) {
        const cursorElm = document.createElement('div')
        cursorElm.classList.add('CodeMirror-cursor')
        cursorElm.classList.add('shadow-cursor')

        const {left, top, bottom} = this.cminstance.charCoords({line, ch})
        cursorElm.style.left = left + 'px'
        cursorElm.style.top = top + 'px'
        cursorElm.style.height = bottom - top + 'px'

        const hue = this.ghostCursors.length * 70
        cursorElm.style.borderLeftColor = `hsl(${hue},90%,50%)`

        this.ghostCursorWrapper.append(cursorElm)
        this.ghostCursors.push(cursorElm)

        // return an id
        return this.ghostCursors.length - 1
      },

      updateShadowCursorLocation (id, line, ch) {
        const cursorElm = this.ghostCursors[id]

        const {left, top, bottom} = this.cminstance.charCoords({line, ch})
        cursorElm.style.left = left + 'px'
        cursorElm.style.top = top + 'px'
        cursorElm.style.height = bottom - top + 'px'
      },

      lock (start, end) {
        for (let line = start; line <= end; line++) {
          this.cminstance.addLineClass(line, 'wrap', 'lock')
        }
      },

      unlock (start, end) {
        for (let line = start; line <= end; line++) {
          this.cminstance.removeLineClass(line, 'wrap', 'lock')
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
    .shadow-cursor{
        /*animation: blinker 1s steps() infinite alternate;*/
    }

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
