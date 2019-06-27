<template>
  <div class="ghostCursor" :style="style" v-if="line > -1"></div>
</template>

<script>
  /**
   * @module Editor/GhostCursor
   * @desc The cursor of another user.
   *
   * @vue-prop {String} username - The username of the owner of the cursor.
   * @vue-prop {String} filepath - The filepath the cursor is in.
   * @vue-prop {Number} line - The line number inside the piece (thus not the global line number) the cursor is at.
   * @vue-prop {String} ch - The character position (thus horizontal position) of the cursor.
   * @vue-prop {Object} backgroundColor - The color of the user and thus also the cursor.
   * @vue-prop {Object} cminstance - The CodeMirror instance of the editor this cursor is in.
   *
   * @vue-data {Number} top - The relative vertical position of the cursor in pixels
   * @vue-data {Number} left - The relative horizontal position of the cursor in pixels
   *
   * @vue-computed {String} color - The recommended text color for the best contrast against the background.
   */
  export default {
    name: 'GhostCursor',
    props: {
      username: String,
      filepath: String,
      line: Number,
      ch: Number,
      backgroundColor: Object,
      cminstance: Object
    },
    data () {
      return {
        top: 0,
        left: 0
      }
    },
    computed: {
      color () {
        return this.backgroundColor.isLight() ? '#151515' : '#fff'
      },

      style () {
        return {
          left: this.left + 'px',
          top: this.top + 'px',
          '--user-name': `'${this.username}'`,
          backgroundColor: this.backgroundColor.string(),
          color: this.color
        }
      },

      gutterWidth () {
        return this.cminstance.getGutterElement().getBoundingClientRect().width
      }
    },
    methods: {
      updateCoords () {
        if (!this.cminstance) return
        const pos = this.cminstance.charCoords({line: this.line, ch: this.ch}, 'local')
        this.left = pos.left + this.gutterWidth
        this.top = pos.top
      }
    },
    watch: {
      line () { this.updateCoords() },
      ch () { this.updateCoords() },
      cminstance () { this.updateCoords() }
    },
    mounted () {
      this.updateCoords()
    }
  }
</script>

<style lang="scss" scoped>
  .ghostCursor {
    position: absolute;
    pointer-events: none;
    height: 1em;
    --hue-color: 170;
    --user-name: 'no';
    width: 2px;
    z-index: 5;

    &:after {
      content: var(--user-name);
      /*color: #333;*/
      /*font-weight: 600;*/
      font-family: 'Source Sans Pro', sans-serif;
      position: absolute;
      display: block;
      height: 1em;
      font-size: 0.6em;
      line-height: 1em;
      padding: 0 2px;
      margin-top: -.8em;
      z-index: 100;
      background-color: inherit;
    }
  }
</style>
