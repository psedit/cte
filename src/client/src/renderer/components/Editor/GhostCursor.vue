<template>
  <div class="ghostCursor" :style="style"></div>
</template>

<script>
  import {getRandomColor} from './RandomColor'

  export default {
    name: 'GhostCursor',
    props: {
      username: String,
      filepath: String,
      line: Number,
      ch: Number,
      cminstance: Object
    },
    data () {
      return {
        top: 0,
        left: 0
      }
    },

    computed: {
      backgroundColor () {
        return getRandomColor(this.username)
      },

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
