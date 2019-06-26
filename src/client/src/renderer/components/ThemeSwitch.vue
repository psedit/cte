<template>
  <div>
    <lightbulb-outline v-if="lightTheme" id="theme-button-on" class="button" @click="turnOff"/>
    <lightbulb v-if="!lightTheme" id="theme-button-off" class="button" @click="turnOn"/>
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
