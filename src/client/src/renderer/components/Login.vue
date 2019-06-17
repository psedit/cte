<template>
  <div>
    <input type="text" name="username" v-model="username">
    <input type="submit" name="send" value="send" @click="sendLogin">
  </div>
</template>

<script>
import connector from '../../main/connector.js'
export default {
  data () {
    return {
      username: ''
    }
  },
  methods: {
    sendLogin () {
      connector.request('login-request', 'login-response', {username: this.username}).then((response) => {
        console.log(response)
        if (response.succeed) {
          this.$store.dispatch('login', this.username)
        } else {
          console.log(response.error)
        }
      })
    }
  }
}
</script>
<style scoped>
</style>