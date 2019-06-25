<template>
  <div ref="cm" class="editor-piece" :class="{editable, open_editor: piece.username === ''}">
    <ghost-cursors ref="ghostCursors" :piece="piece"/>
  </div>
</template>

<script>
  import CodeMirror from 'codemirror/lib/codemirror'
  import 'codemirror/lib/codemirror.css'
  import 'codemirror/theme/monokai.css'
  import 'codemirror/mode/javascript/javascript'
  import 'codemirror/mode/python/python'
  import { edit, indexOffsetRangeSort } from '../../../main/pieceTable'
  import './multiEditor'
  import connector from '../../../main/connector'
  import {getRandomColor} from './RandomColor'
  import GhostCursors from './GhostCursors'

  export default {
    name: 'EditorPiece.vue',
    components: {
      GhostCursors
    },
    props: {
      pieces: Array,
      index: Number,
      dragStart: Object,
      dragEnd: Object
    },

    data () {
      return {
        lang: null
      }
    },

    myPromise: null,
    cminstance: null,
    preText: null,
    startState: null,
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
      this.$emit('mounted', this)
    },
    computed: {
      codeArray () {
        return this.pieces[this.index].text
      },
      code () {
        return this.codeArray.join('').replace(/\n$/g, '')
      },

      piece () {
        return this.pieces[this.index]
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

      firstLineNumber () {
        return this.pieces.slice(0, this.index).reduce((acc, val) => val.text.length + acc, 0) + 1
      },

      pieceDragStart () {
        if (!(this.dragStart || this.dragEnd)) {
          return null
        }
        let start = indexOffsetRangeSort(this.dragStart, this.dragEnd)[0]
        if (start.piece < this.index) {
          return 0
        } else if (start.piece === this.index) {
          return start.line
        }

        return null
      },
      pieceDragLength () {
        const cm = this.$options.cminstance
        if (!(this.dragStart && this.dragEnd)) {
          return -1
        }
        let range = indexOffsetRangeSort(this.dragStart, this.dragEnd)
        let start = range[0]
        let end = range[1]
        if (start.piece > this.index || end.piece < this.index) {
          return -1
        } else if (end.piece > this.index) {
          return cm.lineCount() - this.pieceDragStart
        } else {
          if (start.line < this.index) {
            return end.line + 1
          } else {
            return end.line - start.line + 1
          }
        }
      }
    },

    methods: {
      initializeEditor () {
        if (!this.$options.myPromise) {
          this.$options.myPromise = new Promise(resolve => {
            setTimeout(() => {
              this._initializeEditor()
              resolve(this.$options.cminstance)
            }, 0)
          })

          this.$options.myPromise.then((cm) => this.$refs.ghostCursors.init(cm, this.piece))
        }
        return this.$options.myPromise
      },

      _initializeEditor () {
        if (!window.CodeMirror) window.CodeMirror = CodeMirror
        // debugger
        const cm = CodeMirror(this.$refs.cm, {
          mode: {
            name: 'multi_editor',
            lang: this.lang,
            startState: this.$options.startState
          },
          lineNumbers: true,
          theme: 'monokai',
          smartIndent: true,
          lineWrapping: true,
          showCursorWhenSelecting: true,
          readOnly: !this.editable,
          // inputStyle: 'contenteditable',
          // lineNumberFormatter: this.lineNumberFormatter,
          firstLineNumber: this.firstLineNumber,
          viewportMargin: Infinity,
          cursorBlinkRate: 0,
          gutters: ['user-gutter', 'CodeMirror-linenumbers']
        })

        this.$options.cminstance = cm

        cm.setValue(this.code)

        // cm.getGutterElement().querySelector('.user-gutter').style.backgroundColor = getRandomColor(this.username).string()
        if (this.username) {
          cm.getGutterElement().style.setProperty('--background-color', getRandomColor(this.username).string())
        }
        cm.getGutterElement().setAttribute('title', this.username || 'Click and drag to lock a piece.')
        this.initializeEvents()
      },
      unlock () {
        console.log('hoi')
        connector.request('file-unlock-request', 'file-unlock-response', {
          file_path: this.$store.state.fileTracker.openFile,
          lock_id: this.pieces[this.index].pieceID
        }).then(({succes}) => {
          console.log(succes, 'hoi ik ben')
          if (!succes) {
            console.error('faal')
          }
        })
      },
      setText () {
        const cm = this.$options.cminstance

        const from = {line: 0, ch: 0}
        const lastLine = cm.lastLine()
        const to = {line: lastLine, ch: cm.getLine(lastLine).length}
        cm.replaceRange(this.code, from, to)
      },
      updateDragStart (newDragStart, oldDragStart) {
        const cm = this.$options.cminstance
        cm.clearGutter('user-gutter')
        for (let i = this.pieceDragStart; i < this.pieceDragStart + this.pieceDragLength; i++) {
          cm.setGutterMarker(this.relativeLineToLine(i), 'user-gutter',
            this.gutterSelectMarker())
        }
        // this.$emit('restoreScrollPosition')
      },
      updateDragLength (newDragLength, oldDragLength) {
        const cm = this.$options.cminstance
        cm.clearGutter('user-gutter')
        for (let i = this.pieceDragStart; i < this.pieceDragStart + this.pieceDragLength; i++) {
          cm.setGutterMarker(this.relativeLineToLine(i), 'user-gutter',
            this.gutterSelectMarker())
        }
        // this.$emit('restoreScrollPosition')
      },
      lineToRelativeLine (line) {
        const cm = this.$options.cminstance
        return line - cm.firstLine()
      },
      relativeLineToLine (line) {
        const cm = this.$options.cminstance
        return (cm.firstLine() + line)
      },

      gutterSelectMarker () {
        const marker = document.createElement('div')
        marker.classList.add('lock-gutter-marker')
        marker.innerHTML = '●'
        return marker
      },

      initializeEvents () {
        const cm = this.$options.cminstance

        cm.on('blur', () => {
          // cm.setCursor({line: 0, ch: 0}, {
          //   scroll: false
          // })
        })
        cm.on('focus', () => {
          const cursorPos = cm.doc.getCursor()
          connector.send('cursor-move', {
            file_path: this.$store.state.fileTracker.openFile,
            piece_id: this.pieces[this.index].pieceID,
            offset: cursorPos.line,
            column: cursorPos.ch
          })
        })

        cm.on('update', () => {
          this.$emit('update')
        })

        cm.on('viewportChange', () => {
          this.$emit('viewportChange', this.index)
        })

        cm.on('scrollCursorIntoView', (_, e) => {
          e.preventDefault()
        })

        if (this.editable) {
          cm.on('changes', ({cminstance}) => {
            const value = cm.getValue()
            const content = value.split('\n').map(val => val + '\n')
            const newPieceTable = edit(this.pieceTable, this.pieces[this.index].pieceID, content)
            this.$store.dispatch('updatePieceTable', newPieceTable)

            connector.send('file-delta', {
              file_path: this.$store.state.fileTracker.openFile,
              piece_uuid: this.pieces[this.index].pieceID,
              content: value
            })
          })

          cm.on('cursorActivity', () => {
            const cursorPos = cm.doc.getCursor()

            connector.send('cursor-move', {
              file_path: this.$store.state.fileTracker.openFile,
              piece_id: this.pieces[this.index].pieceID,
              offset: cursorPos.line,
              column: cursorPos.ch
            })
          })
        }

        const gutter = cm.getGutterElement()
        if (!this.editable) {
          gutter.addEventListener('mousedown', (e) => {
            const line = cm.lineAtHeight(e.pageY)
            const relLine = this.lineToRelativeLine(line)
            this.$emit('lockDragStart', relLine, this.index, e)
          })
          gutter.addEventListener('mousemove', (e) => {
            const line = cm.lineAtHeight(e.pageY)
            const relLine = this.lineToRelativeLine(line)
            this.$emit('lockDragUpdate', relLine, this.index, e)
          })
          gutter.addEventListener('mouseup', (e) => {
            const line = cm.lineAtHeight(e.pageY)
            const relLine = this.lineToRelativeLine(line)
            this.$emit('lockDragEnd', relLine, this.index, e)
          })
        }
        if (this.editable) {
          gutter.addEventListener('contextmenu', this.unlock)
        }
      },

      updateLineNumbers () {
        const cm = this.$options.cminstance
        cm.setOption('firstLineNumber', this.firstLineNumber)
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
    box-shadow: 0 0 3em 1em var(--background-color);
  }
}

.open_editor {
  .user-gutter {
    box-shadow: none;
  }
}

.user-gutter {
  width: 1em;
  background-color: var(--background-color, rgba(255, 255, 255, 0.5));
}

.lock-gutter-marker {
  width: 100%;
  background-color: #fff;
  pointer-events: none;
  position: absolute;

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
