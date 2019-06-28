<template>
  <div ref="cm" class="editor-piece" :class="{editable, open_editor: piece.username === ''}">
    <ghost-cursors ref="ghostCursors" :piece="piece"/>
    <add-piece-button :pieceID="piece.pieceID"/>
  </div>
</template>

<script>
  import CodeMirror from 'codemirror/lib/codemirror'
  import 'codemirror/lib/codemirror.css'
  import 'codemirror/theme/monokai.css'
  import 'codemirror/mode/javascript/javascript'
  import 'codemirror/mode/python/python'
  import 'codemirror/addon/hint/show-hint'
  import 'codemirror/addon/hint/show-hint.css'
  import 'codemirror/addon/hint/javascript-hint'
  import 'codemirror/addon/edit/closebrackets'
  import 'codemirror/addon/edit/matchbrackets'
  import 'codemirror/addon/selection/active-line'
  import { edit, indexOffsetRangeSort } from '../../../main/pieceTable'
  import './multiEditor'
  import connector from '../../../main/connector'
  import {getRandomColor} from './RandomColor'
  import GhostCursors from './GhostCursors'
  import AddPieceButton from './AddPieceButton'

  /**
   * @module Editor/EditorPiece
   * @desc Represents a piece of the editor.
   *       Handles the actual editing behaviour.
   *
   * @vue-prop {Piece[]} pieces - The piece table
   * @vue-prop {Number} index - The index of the current piece.
   * @vue-prop {Object} dragStart - The start position of dragging.
   * @vue-prop {Object} dragStop - The stop position of dragging.
   * @vue-prop {Boolean} theme - If true, the theme should be a light theme, otherwise a dark theme.
   *
   * @vue-data {String} lang - The language of the code.
   *
   * @vue-computed {String[]} codeArray - The code of this piece with lines separated in items in the array.
   * @vue-computed {String} code - The code of this piece as one continuous string.
   * @vue-computed {Piece} piece - The piece of the piece table that this editor represents.
   * @vue-computed {String} username - The owner of the piece. An empty string if there is no owner.
   * @vue-computed {Boolean} editable - If the piece should be editable or that it should be read only.
   * @vue-computed {PieceTable} pieceTable - The full piece table.
   * @vue-computed {Number | null} pieceDragStart - The line where the user started dragging in the lock-gutter.
   * @vue-computed {Number} pieceDragLength - The length of the lock the user is currently dragging.
   */
  export default {
    name: 'EditorPiece',
    components: {
      GhostCursors,
      AddPieceButton
    },
    props: {
      pieces: Array,
      index: Number,
      dragStart: Object,
      dragEnd: Object,
      /* true: dark
       * false: light
       */
      theme: Boolean
    },
    /**
   */
    data () {
      return {
        lang: null,
        focus: false
      }
    },

    /**
     * @alias $options.myPromise
     */
    myPromise: null,
    /**
     * @alias $options.cminstance
     */
    cminstance: null,
    /** @type Object | null */
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
      },
      theme (newTheme) {
        this.updateTheme(newTheme)
      }
    },
    mounted () {
      this.$emit('mounted', this)
      document.documentElement.style.setProperty('--user-color', getRandomColor(this.$store.state.user.username))
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
      /**
       * Initializes a codemirror editor.
       * Also initiates the ghostcursors for this piece after
       * codemirror has been initiated.
       *
       * Promise is made only once.
       *
       * @returns {Promise<CodeMirror>} The promise resolved with the made CodeMirror instance.
       */
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

      /**
       * Changes the theme between a light and dark theme as set by this.theme.
       */
      updateTheme () {
        const cm = this.$options.cminstance
        if (this.theme) {
          cm.setOption('theme', 'default')
        } else {
          cm.setOption('theme', 'monokai')
        }
      },

      /**
       * Initializes the editor.
       *
       * Makes a CodeMirror instance and sets all the configuration.
       * Also makes the lock-gutter and calls to initialize all the events.
       * @private
       */
      _initializeEditor () {
        let initTheme = 'monokai'
        if (this.theme) {
          initTheme = 'default'
        }
        if (!window.CodeMirror) window.CodeMirror = CodeMirror
        const cm = CodeMirror(this.$refs.cm, {
          mode: {
            name: 'multi_editor',
            lang: this.lang,
            startState: this.$options.startState
          },
          lineNumbers: true,
          theme: initTheme,
          smartIndent: true,
          lineWrapping: true,
          showCursorWhenSelecting: true,
          readOnly: !this.editable,
          firstLineNumber: this.firstLineNumber,
          viewportMargin: Infinity,
          cursorBlinkRate: 0,
          autoCloseBrackets: true,
          styleActiveLine: true,
          gutters: ['user-gutter', 'CodeMirror-linenumbers']
        })

        this.$options.cminstance = cm

        if (this.lang === 'javascript') {
          cm.addKeyMap({'Ctrl-Space': 'autocomplete'}, false)
          cm.setOption('matchBrackets', true)
          cm.setOption('autoCloseBrackets ', true)
        }
        cm.setValue(this.code)

        if (this.username) {
          cm.getGutterElement().style.setProperty('--background-color', getRandomColor(this.username).string())
        }
        cm.getGutterElement().setAttribute('title', this.username.replace(/[0-9]/g, '').replace(/_/g, '') || 'Click and drag to lock a piece.')
        this.initializeEvents()
      },

      /**
       * Does an request to unlock the current piece.
       */
      unlock () {
        connector.request('file-unlock-request', 'file-unlock-response', {
          file_path: this.$store.state.fileTracker.openFile,
          lock_id: this.pieces[this.index].pieceID
        })
      },

      /**
       * Updates current code to be the same as this.code
       */
      setText () {
        const cm = this.$options.cminstance

        const from = {line: 0, ch: 0}
        const lastLine = cm.lastLine()
        const to = {line: lastLine, ch: cm.getLine(lastLine).length}
        // Use replaceRange instead of setValue to prevent scrolling.
        cm.replaceRange(this.code, from, to)
      },

      /**
       * Changes the drag start position in the lock gutter.
       *
       * @param newDragStart The current position where the user is dragging.
       * @param oldDragStart The previous position where the user is dragging.
       */
      updateDragStart (newDragStart, oldDragStart) {
        const cm = this.$options.cminstance
        cm.clearGutter('user-gutter')
        for (let i = this.pieceDragStart; i < this.pieceDragStart + this.pieceDragLength; i++) {
          cm.setGutterMarker(this.relativeLineToLine(i), 'user-gutter',
            this.gutterSelectMarker())
        }
      },

      /**
       * Changes the drag length position in the lock gutter.
       * @param newDragLength The current length of the lock the user is dragging.
       * @param oldDragLength The previous length of the lock the user is dragging.
       */
      updateDragLength (newDragLength, oldDragLength) {
        const cm = this.$options.cminstance
        cm.clearGutter('user-gutter')
        for (let i = this.pieceDragStart; i < this.pieceDragStart + this.pieceDragLength; i++) {
          cm.setGutterMarker(this.relativeLineToLine(i), 'user-gutter',
            this.gutterSelectMarker())
        }
      },

      /**
       *
       * @deprecated Because changes will return line again.
       * @param line
       * @returns {number}
       */
      lineToRelativeLine (line) {
        const cm = this.$options.cminstance
        return line - cm.firstLine()
      },
      /**
       *
       * @deprecated Because changes will return line again.
       * @param line
       * @returns {number}
       */
      relativeLineToLine (line) {
        const cm = this.$options.cminstance
        return (cm.firstLine() + line)
      },

      /**
       * Makes an marker element for highlighting the dragged lock region.
       * @returns {HTMLElement} - The element with a class lock-gutter-marker.
       */
      gutterSelectMarker () {
        const marker = document.createElement('div')
        marker.classList.add('lock-gutter-marker')
        marker.innerHTML = '&nbsp;'
        return marker
      },

      /**
       * Initializes all events.
       */
      initializeEvents () {
        const cm = this.$options.cminstance

        cm.on('blur', () => {
          this.focus = false
        })

        cm.on('focus', () => {
          this.focus = true
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

        cm.on('cursorActivity', () => {
          if (!this.focus) return
          const cursorPos = cm.doc.getCursor()

          this.$emit('cursorActivity', cm.cursorCoords(true, 'page').top)

          connector.send('cursor-move', {
            file_path: this.$store.state.fileTracker.openFile,
            piece_id: this.pieces[this.index].pieceID,
            offset: cursorPos.line,
            column: cursorPos.ch
          })
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
              content: content.join('')
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

      /**
       * Changes the first line to this.$options.firstLineNumber
       */
      updateLineNumbers () {
        const cm = this.$options.cminstance
        cm.setOption('firstLineNumber', this.firstLineNumber)
      }
    }
  }
</script>

<style lang="scss">
@import url(https://cdn.jsdelivr.net/gh/tonsky/FiraCode@1.206/distr/fira_code.css);
.editor-piece {
  &:last-child {
    .CodeMirror {
      height: 100%;
    }
  }
  border-bottom: 1px rgba(255, 255, 255, 0.2) dashed;
  position: relative;
}

.CodeMirror {
  height: auto;
  font-family: 'Fira Code', monospace;
  font-variant-ligatures: contextual;
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

.CodeMirror-cursor {
  border-left: 4px solid var(--user-color) !important;
}

.user-gutter {
  width: 1em;
  background-color: var(--background-color, #aaa);
}

.lock-gutter-marker {
  width: 100%;
  background-color: #fff;
  pointer-events: none;
  position: absolute;
}

.CodeMirror-linenumbers {
  min-width: 3em;
}

.CodeMirror:not(.CodeMirror-focused) .CodeMirror-activeline-background{
  background-color: transparent;
}

.CodeMirror-activeline-gutter {
  pointer-events: none;
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
