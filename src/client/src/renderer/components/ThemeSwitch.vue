<template>
  <div class="theme-switch" :class="{'theme-switch-on' : lightTheme}" :title="tooltip">
    <lightbulb-outline v-if="lightTheme" id="theme-button-on" class="button" @click="turnOff" decorative/>
    <lightbulb v-if="!lightTheme" id="theme-button-off" class="button" @click="turnOn" decorative/>
  </div>
</template>

<script>
import LightbulbOutline from 'vue-material-design-icons/LightbulbOutline'
import Lightbulb from 'vue-material-design-icons/Lightbulb'
export default {
  name: 'theme-button',
  components: {
    LightbulbOutline,
    Lightbulb
  },
  data () {
    return {
      lightTheme: false
    }
  },
  computed: {
    tooltip () {
      return `Switch to ${this.lightTheme ? 'light' : 'dark'} theme.`
    }
  },
  methods: {
    turnOn () {
      this.lightTheme = true
      this.$emit('theme-change', this.lightTheme)
    },
    turnOff () {
      this.lightTheme = false
      this.$emit('theme-change', this.lightTheme)
    }
  }
}
</script>

<style scoped lang="scss">
  .theme-switch {
    border: 1px white solid;
    background-color: #222;
    color: #fff;

    display: block;
    position: fixed;
    right: 1.5em;
    top: 3em;
    width: 2em;
    height: 2em;
    border-radius: 1em;
    text-align: center;
    line-height: 2em;
    z-index: 10;
    cursor: pointer;

    &-on {
      border: 1px #222 solid;
      color: #222;
      background-color: #f9cd0b;
    }

    .button:before {
      content: '';
      position: absolute;
      width: 2em;
      height: 2em;
      margin: -.5em 0 0 -.5em;
    }
  }
</style>
