<template>
  <div class="template">
      <img src="@/assets/logoGroot.png" alt="" class="logo">
      <div class="text"><== Select a file</div>
  </div>
</template>

<script>
  export default {
    name: 'Placeholder'
  }
</script>

<style scoped lang="scss">
  .template {
    position: relative;
  }
  .logo {
    filter: drop-shadow(0 0 0.1em rgba(#333, 0.3));
    width: 50%;
    position: absolute;
    top: 25%;
    left: 25%;
  }
  .text {
    position: absolute;
    top: 60%;
    left: 25%;

  }
</style>
