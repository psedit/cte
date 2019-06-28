<template>
  <div v-show="max" class="track" ref="track" :style="{height: `${viewportHeight}px`}">
      <div class="thumb"
           :style="{
              top: `${top}px`,
              height: `${thumbHeight}px`
            }"
           @mousedown="mousedown"
           @mouseup="mouseup"
      ></div>
  </div>
</template>

<script>
  /**
   * @module ScrollBar
   * @desc Contains the logic for the scrollbar.
   * @vue-data {number} viewportHeight the height of the viewport
   * @vue-data {number} max the height of your document
   * @vue-data {boolean} dragging whether the user is dragging the scrollbar
   * @vue-computed {number} thumbHeight the height of the dragable part of the scrollbar
   * @vue-computed {number} top the position of the thumbbar
   */
  export default {
    name: 'ScrollBar',
    props: {
      value: Number
    },
    data () {
      return {
        viewportHeight: 0,
        max: 0,
        dragging: false
      }
    },
    computed: {
      thumbHeight () {
        return this.viewportHeight / this.max * this.viewportHeight
      },

      top () {
        return this.value / this.max * (this.viewportHeight - this.thumbHeight)
      }
    },

    methods: {
      /**
       * Renders the scrollbar
       */
      render () {
        const editor = this.$parent
        this.viewportHeight = editor.$el.clientHeight
        this.max = editor.$refs.editorPiecesList.clientHeight

        requestAnimationFrame(() => {
          this.render()
        })
      },
      /**
       * Sets the dragging state to false.
       */
      mouseup () {
        this.dragging = false
      },
      /**
       * Emits when the position when the user is dragging
       * @param {Object} event a mouse move event
       */
      mousemove (event) {
        if (this.dragging) {
          const top = this.top + event.movementY
          const val = top / (this.viewportHeight - this.thumbHeight) * this.max
          this.$emit('input', val)
        }
      },
      /**
       * Sets the dragging state to true and prevents the default.
       * @param event a mouse down event
       */
      mousedown (event) {
        this.dragging = true
        event.preventDefault()
      }
    },

    mounted () {
      this.render()
      addEventListener('mouseup', this.mouseup)
      addEventListener('mousemove', this.mousemove)
    }
  }
</script>

<style scoped lang="scss">
.track {
  z-index: 10;
  font-size: 1.3em;
  position: fixed;
  width: .5em;
  right: 0;
  top: 2em;
}

.thumb {
  position: relative;
  width: 100%;
  border-radius: .25em;
  background-color: #999;
}
</style>
