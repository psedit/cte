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
      render () {
        const editor = this.$parent
        this.viewportHeight = editor.$el.clientHeight
        this.max = editor.$refs.editorPiecesList.clientHeight

        requestAnimationFrame(() => {
          this.render()
        })
      },

      mouseup () {
        this.dragging = false
      },

      mousemove (event) {
        if (this.dragging) {
          const top = this.top + event.movementY
          const val = top / (this.viewportHeight - this.thumbHeight) * this.max
          this.$emit('input', val)
        }
      },

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
  /*background-color: rgba(30, 30, 30, 0.2);*/
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
