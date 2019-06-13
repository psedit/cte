<template>
  <div class="ghostCursor" :style="style"></div>
</template>

<script>
  import Color from 'color'

  const pearsonTable = [...new Array(360)].map((_, i) => i).sort(() => 0.5 - Math.random())

  export default {
    name: 'GhostCursor',
    props: {
      username: String,
      filepath: String,
      line: Number,
      ch: Number,
      cminstance: Object
    },

    computed: {
      backgroundColor () {
        // Peason hash to generate hue
        const hue = this.username.split('').reduce((hash, char) => {
          return pearsonTable[(hash + char.charCodeAt(0)) % (pearsonTable.length - 1)]
        }, this.username.length % (pearsonTable.length - 1))
        return Color.hsl(hue, 90, 50)
      },

      color () {
        console.log(this.backgroundColor.luminosity(), this.backgroundColor.isLight())
        return this.backgroundColor.isLight() ? '#151515' : '#fff'
      },

      style () {
        const {top, left} = this.cminstance.charCoords({line: this.line, ch: this.ch}, 'local')
        return {
          left: left + 'px',
          top: top + 'px',
          '--user-name': `'${this.username}'`,
          backgroundColor: this.backgroundColor.string(),
          color: this.color
        }
      }
    }
  }
</script>

<style lang="scss" scoped>
  .ghostCursor {
    position: absolute;
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
