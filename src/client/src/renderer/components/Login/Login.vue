<template>
  <div>
    <input type="text" name="username" v-model="username">
    <input type="password" name="password" v-model="password">
    <input type="submit" name="send" value="send">
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
  }
}
</script>
<style scoped>
</style>