<template>
  <div>
    <input type="text" name="username" v-model="username">
    <input type="password" name="password" v-model="password">
    <input type="submit" name="send" value="send" @click="sendLogin">
  </div>
</template>

<script>
export default {
  data () {
    return {
      username: '',
      password: ''
    }
  },
  methods: {
    sendLogin () {
      console.log(this.username, this.password)
    }
  }
}
</script>
<style scoped>
</style>