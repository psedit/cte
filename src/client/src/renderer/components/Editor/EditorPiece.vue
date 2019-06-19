<template>
  <div ref="cm" class="editor-piece" :class="{editable}"></div>
</template>

<script>
  import CodeMirror from 'codemirror/lib/codemirror'
  import 'codemirror/lib/codemirror.css'
  import 'codemirror/theme/monokai.css'
  import 'codemirror/mode/javascript/javascript'
  import 'codemirror/mode/python/python'
  import { edit } from '../../../main/pieceTable'
  import connector from '../../../main/connector'
  import {getRandomColor} from './RandomColor'

  export default {
    name: 'EditorPiece.vue',
    props: {
      pieces: Array,
      index: Number
    },

    data () {
      return {
      }
    },

    cminstance: null,
    preText: null,
    watch: {
      code (val) {
        if (!this.editable) {
          this.setText()
        }
      }
    },
    mounted () {
      setTimeout(() => this.initializeEditor(), 0)
    },
    computed: {
      textPiecesArray () {
        return this.pieces.map(piece => piece.text)
      },
      textPieces () {
        return this.textPiecesArray.join('').replace(/\n$/, '')
      },

      preCodeArray () {
        return this.pieces.slice(0, this.index).reduce((acc, piece) => {
          return acc.concat(piece.text)
        }, [])
      },
      preCode () {
        return this.preCodeArray.join('').replace(/\n$/, '')
      },

      codeArray () {
        return this.pieces[this.index].text
      },
      code () {
        return this.codeArray.join('').replace(/\n$/, '')
      },

      username () {
        return this.pieces[this.index].username
      },
      editable () {
        return this.$store.state.user.username === this.username
      },
      pieceTable () {
        return this.$store.state.fileTracker.pieceTable
      }
    },

    methods: {
      initializeEditor () {
        const cm = CodeMirror(this.$refs.cm, {
          mode: 'javascript',
          lineNumbers: true,
          theme: 'monokai',
          smartIndent: true,
          lineWrapping: true,
          showCursorWhenSelecting: true,
          readOnly: !this.editable,
          // inputStyle: 'contenteditable',
          lineNumberFormatter: this.lineNumberFormatter,
          viewportMargin: Infinity,
          cursorBlinkRate: 0,
          gutters: ['user-gutter', 'CodeMirror-linenumbers'],
          extraKeys: {
            'Alt-R': () => {
              this.updatePreviousText()
            }
          }
        })

        this.$options.cminstance = cm

        cm.setValue(this.code)
        if (this.index !== 0) {
          this.addPreviousText()
        }

        cm.getGutterElement().querySelector('.user-gutter').style.backgroundColor = getRandomColor(this.username).string()
        cm.getGutterElement().setAttribute('title', this.username)
        this.initializeEvents()
      },
      setText () {
        const cm = this.$options.cminstance

        cm.setValue(this.code)
        if (this.index !== 0) {
          this.addPreviousText()
        }
      },
      addPreviousText () {
        if (this.preCode === '') return

        const cm = this.$options.cminstance

        this.insertText(this.preCode + '\n', {line: 0, ch: 0})

        const lines = this.preCodeArray.length
        this.$options.preText = cm.markText({line: 0, ch: 0}, {line: lines, ch: 0}, {
          collapsed: true,
          inclusiveLeft: true,
          inclusiveRight: false,
          selectLeft: false,
          selectRight: true,
          atomic: true,
          readOnly: true
        })
      },
      updatePreviousText () {
        if (this.index === 0) return
        const range = this.$options.preText.find()
        this.$options.preText.clear()
        this.deleteText(range.from, range.to)
        this.addPreviousText()
        // this.$options.preText.changed()
        // console.log(this.$options.cminstance.getValue())
      },

      lineToRelativeLine (line) {
        if (line === 0) return 0
        const mark = this.$options.cminstance.getAllMarks()[0]
        if (!mark) return line

        return line - mark.lines.length + 1
      },
      relativeLineToLine (line) {
        if (line === 0) return 0
        const mark = this.$options.cminstance.getAllMarks()[0]
        if (!mark) return line

        return line + mark.lines.length - 1
      },

      initializeEvents () {
        const cm = this.$options.cminstance

        cm.on('blur', () => {
          cm.setCursor({line: 0, ch: 0}, {
            scroll: false
          })
        })

        cm.on('scrollCursorIntoView', (_, e) => {
          e.preventDefault()
        })

        if (this.editable) {
          cm.on('changes', ({cminstance}) => {
            const value = cm.getValue().slice(this.preCode.length)
            // console.log(value)
            const content = value.split('\n').map(val => val + '\n')
            const newPieceTable = edit(this.pieceTable, this.pieces[this.index].pieceID, content)
            this.$store.dispatch('updatePieceTable', newPieceTable)

            connector.send('file-delta', {
              file_path: this.$store.state.fileTracker.openFile,
              piece_uuid: this.pieces[this.index].pieceID,
              content: value
            })
          })
        }

        const gutter = cm.getGutterElement()
        gutter.addEventListener('mousedown', (e) => {
          const line = cm.lineAtHeight(e.pageY)
          const relLine = this.lineToRelativeLine(line)
          // console.log('mouse up at', line)
          this.$emit('lockDragStart', relLine, this.index, e)
        })
        gutter.addEventListener('mouseup', (e) => {
          const line = cm.lineAtHeight(e.pageY)
          const relLine = this.lineToRelativeLine(line)
          // console.log('mouse down at', line)
          this.$emit('lockDragEnd', relLine, this.index, e)
        })
      },

      insertText (text, pos) {
        const cm = this.$options.cminstance
        pos.line = this.relativeLineToLine(pos.line)
        cm.replaceRange(text, pos, pos, {
          scroll: true
        })
      },

      deleteText (from, to) {
        from.line = this.relativeLineToLine(from.line)
        to.line = this.relativeLineToLine(to.line)
        const cm = this.$options.cminstance
        cm.replaceRange('', from, to, {
          scroll: true
        })
      },

      lineNumberFormatter (line) {
        if (line === 1 && this.index !== 0) {
          return (this.preCodeArray.length + 1).toString()
        }
        return (line).toString()
      }
    }
  }
</script>

<style lang="scss">
.editor-piece {
  &:last-child {
    .CodeMirror {
      height: 100%;
    }
  }
  border-bottom: 1px rgba(255, 255, 255, 0.2) dashed;
}

.CodeMirror {
  height: auto;
}

.CodeMirror-lines {
  min-height: unset !important;
  padding: 0;
}
.editable {
  .CodeMirror-cursor {
    animation: blink 1s step-end infinite;
  }
  .user-gutter {
    box-shadow: 0 0 3em 1em rgba(0, 256, 30, 0.6);
  }
}

.user-gutter {
  width: 1em;
}

@keyframes blink {
  from,
  to {
    opacity: 1;
  }

  50% {
    opacity: 0;
  }
}
</style>
