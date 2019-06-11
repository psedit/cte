<template>
  <div class="codemirror-wrapper" ref="wrapper"></div>
</template>

<script>
  import CodeMirror from 'codemirror/lib/codemirror'
  import 'codemirror/lib/codemirror.css'
  import 'codemirror/theme/cobalt.css'
  import 'codemirror/mode/javascript/javascript'
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
        ghostCursorWrapper: null,
        ghostCursors: []
      }
    },

    props: {
      value: String
    },

    watch: {
      value (newVal, oldVal) { // watch it
        this.cminstance.setValue(this.value)
        console.log('Prop changed: ', newVal, ' | was: ', oldVal)
      }
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
          /* Cancel change if it was initiated by a user outside of their
           * locked sections */
          if (change.origin !== 'setValue' && info.wrapClass !== 'lock') {
            change.cancel()
          }
        })

        this.codemirror.on('update', () => {
          this.updateCursors()
        })

        // prevents funky dynamic rendering
        this.refresh()
      },

      updateCursors () {
        for (let cursor of this.ghostCursors) {
          const line = cursor.dataset.line
          const ch = cursor.dataset.ch
          const id = cursor.dataset.id
          this.updateShadowCursorLocation(Number(id), line, ch)
        }
      },

      addShadowCursor (line, ch, userName) {
        const cursorElm = document.createElement('div')
        cursorElm.classList.add('shadow-cursor')

        cursorElm.dataset.line = line
        cursorElm.dataset.ch = ch
        cursorElm.dataset.username = userName
        cursorElm.dataset.id = this.ghostCursors.length.toString()

        cursorElm.style.height = this.cminstance.display.cachedTextHeight + 'px'

        const hue = this.ghostCursors.length * 70
        cursorElm.style.setProperty('--hue-color', hue)
        cursorElm.style.setProperty('--user-name', `'${userName}'`)
        cursorElm.style.borderLeftColor = `hsl(${hue},90%,50%)`

        this.ghostCursors.push(cursorElm)
        this.cminstance.addWidget({line, ch}, cursorElm, false)

        // return an id
        return this.ghostCursors.length - 1
      },

      updateShadowCursorLocation (id, line, ch) {
        const cursorElm = this.ghostCursors[id]

        const {left, top, bottom} = this.cminstance.charCoords({line, ch})
        const {x} = this.cminstance.display.lineSpace.getBoundingClientRect()

        cursorElm.style.left = left - x + 'px'
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
  .shadow-cursor {
    --hue-color: 180;
    --user-name: 'no';
    position: absolute !important;
    width: 2px;
    background-color: hsl(var(--hue-color), 100%, 50%);

    &:after {
      content: var(--user-name);
      position: absolute;
      display: block;
      height: 1em;
      font-size: 0.8em;
      padding: 0 2px;
      margin-top: -.3em;
      z-index: 100;
      background-color: hsl(var(--hue-color), 90%, 40%);
    }
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
