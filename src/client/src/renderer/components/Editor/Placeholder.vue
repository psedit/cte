<template>
  <div class="template">
    <div class="logo"></div>
    <!--<img src="@/assets/logoGroot.png" alt="" class="logo">-->
    <div class="text">⇚ Select a file</div>
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
    background-image: url("../../assets/logoGroot.png");
    background-repeat: no-repeat;
    background-size: contain;
    background-position: center;
    filter: drop-shadow(0 0 0.1em rgba(#555, 0.9));
    height: 50%;
    width: 50%;
    position: absolute;
    top: 20%;
    left: 25%;
  }
  .text {
    position: absolute;
    bottom: 10%;
    width: 100%;
    color: #999;

  }
</style>
