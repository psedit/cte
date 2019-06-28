<template>
  <div class="template">
    <div class="logo"></div>
    <div class="text">⇚ Select a file</div>
  </div>
</template>

<script>
  /**
   * @module Placeholder
   * @desc Placeholder contains the content that gets shown, when the editor is not opened.
   */
  export default {
    name: 'Placeholder'
  }
</script>

<style scoped lang="scss">
  .template {
    position: relative;
    font-size: 3em;
    height: 100%;
    width: 100%;
    line-height: 100%;
    color: #555;
    text-align: center;
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
