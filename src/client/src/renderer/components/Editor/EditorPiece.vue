<template>
  <div ref="cm" class="editor-piece" :class="{editable}"></div>
</template>

<script>
  import CodeMirror from 'codemirror/lib/codemirror'
  import 'codemirror/lib/codemirror.css'
  import 'codemirror/theme/monokai.css'
  import 'codemirror/mode/javascript/javascript'
  import 'codemirror/mode/python/python'
  import { edit, indexOffsetRangeSort } from '../../../main/pieceTable'
  import connector from '../../../main/connector'
  import {getRandomColor} from './RandomColor'

  export default {
    name: 'EditorPiece.vue',
    props: {
      pieces: Array,
      index: Number,
      dragStart: Object,
      dragEnd: Object
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
      },
      pieceDragStart: function (newDragStart, oldDragStart) {
        this.updateDragStart(oldDragStart, newDragStart)
      },
      pieceDragLength: function (newDragEnd, oldDragEnd) {
        this.updateDragLength(oldDragEnd, newDragEnd)
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
      },

      pieceDragStart () {
        // console.log(this.dragStart, this.dragEnd)
        if (!(this.dragStart || this.dragEnd)) {
          return null
        }
        // let range = indexOffsetRangeSort(this.dragStart, this.dragEnd)[0]
        // console.log(range)
        let start = indexOffsetRangeSort(this.dragStart, this.dragEnd)[0]
        console.log('pieceDragStart()', start.line, this.dragStart.line, this.dragEnd.line, indexOffsetRangeSort(this.dragStart, this.dragEnd))
        if (start.piece < this.index) {
          return 0
        } else if (start.piece === this.index) {
          return start.line
        }
  
        return null
      },
      pieceDragLength () {
        if (!(this.dragStart && this.dragEnd)) {
          return 0
        }
        let range = indexOffsetRangeSort(this.dragStart, this.dragEnd)
        let start = range[0]
        let end = range[1]
        if (start.piece > this.index) {
          return 0
        } else if (end.piece > this.index) {
          return this.textPiecesArray.length
        } else {
          if (start.offset < this.index) {
            console.log('pieceDragLength()', end.line + 1)
            return end.line + 1
          } else {
            console.log('pieceDragLength()', end.line - start.line + 1)
            return end.line - start.line + 1
          }
        }
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

      updateDragStart (newDragStart, oldDragStart) {
        const cm = this.$options.cminstance
        // if (newDragStart === null) {
        //   cm.clearGutter('user-gutter')
        // } else {
        //   if (newDragStart < oldDragStart) {
        //     /* Extend highlight to include earlier start */
        //     for (let i = newDragStart; i < oldDragStart; i++) {
        //       cm.setGutterMarker(this.relativeLineToLine(i), 'user-gutter',
        //         this.gutterSelectMarker())
        //       console.log(`setting marker at ${this.index}:${i}:${this.relativeLineToLine(i)}`)
        //     }
        //   } else if (oldDragStart < newDragStart) {
        //     for (let i = newDragStart; i < oldDragStart; i++) {
        //       cm.setGutterMarker(this.relativeLineToLine(i), 'user-gutter',
        //         null)
        //       console.log(`unsetting marker at ${this.index}:${i}:${this.relativeLineToLine(i)}`)
        //     }
        //   }
        // }
        cm.clearGutter('user-gutter')
        console.log(`drag ${this.pieceDragStart}:${this.pieceDragLength}`)
        for (let i = this.pieceDragStart; i < this.pieceDragStart + this.pieceDragLength; i++) {
          // console.log(`setting marker at ${this.index}:${i}:${this.relativeLineToLine(i)}`)
          cm.setGutterMarker(this.relativeLineToLine(i), 'user-gutter',
            this.gutterSelectMarker())
        }
      },
      updateDragLength (newDragLength, oldDragLength) {
        const cm = this.$options.cminstance
        // if (newDragLength === null || newDragLength === 0) {
        //   cm.clearGutter('user-gutter')
        // } else {
        //   if (newDragLength < oldDragLength) {
        //     /* Extend highlight to include earlier start */
        //     for (let i = this.pieceDragStart; i < this.pieceDragStart + this.pieceDragLength; i++) {
        //       cm.setGutterMarker(this.relativeLineToLine(i), 'user-gutter',
        //         this.gutterSelectMarker())
        //       console.log(`setting marker at ${this.index}:${i}:${this.relativeLineToLine(i)}`)
        //     }
        //   } else if (oldDragLength < newDragLength) {
        //     for (let i = this.pieceDragStart + newDragLength; i < this.pieceDragStart + oldDragLength; i++) {
        //       cm.setGutterMarker(this.relativeLineToLine(i), 'user-gutter',
        //         null)
        //       console.log(`unsetting marker at ${this.index}:${i}:${this.relativeLineToLine(i)}`)
        //     }
        //   }
        // }
        cm.clearGutter('user-gutter')
        console.log(`drag ${this.pieceDragStart}:${this.pieceDragLength}`)
        for (let i = this.pieceDragStart; i < this.pieceDragStart + this.pieceDragLength; i++) {
          // console.log(`setting marker at ${this.index}:${i}:${this.relativeLineToLine(i)}`)
          cm.setGutterMarker(this.relativeLineToLine(i), 'user-gutter',
            this.gutterSelectMarker())
        }
      },

      lineToRelativeLine (line) {
        if (line === 0) return 0
        const mark = this.$options.cminstance.getAllMarks()[0]
        if (!mark) return line

        return line - mark.lines.length + 1
      },
      relativeLineToLine (line) {
        // if (line === 0) return 0
        // const mark = this.$options.cminstance.getAllMarks()[0]
        // if (!mark) return line

        // return line + mark.lines.length - 1
        return (this.preCodeArray.length + line)
      },

      gutterSelectMarker () {
        var marker = document.createElement('div')
        marker.style.backgroundColor = 'white'
        // marker.style.cssText = 'backgroundColor: white; pointer-events: none'
        marker.style.pointerEvents = 'none'
        marker.style.position = 'absolute'
        marker.style.width = '100%'
        marker.innerHTML = '●'
        return marker
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
        // const gutterId = cm.getGutterElement().gutterId
        gutter.addEventListener('mousedown', (e) => {
          const line = cm.lineAtHeight(e.pageY)
          const relLine = this.lineToRelativeLine(line)
          // console.log('mouse up at', line)
          this.$emit('lockDragStart', relLine, this.index, e)
        })
        gutter.addEventListener('mousemove', (e) => {
          const line = cm.lineAtHeight(e.pageY)
          const relLine = this.lineToRelativeLine(line)
          // console.log('mousemove at', relLine, line)
          // cm.setGutterMarker(line, 'user-gutter', this.gutterSelectMarker())
          this.$emit('lockDragUpdate', relLine, this.index, e)
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
