<template>
  <div class="tabnav">
    <ul id="tab-list">
      <li v-for="file in file_paths" class="tab" @click="tabClick(file)">
        {{ file }}
      </li>
    </ul>
    <!-- [insert tab bar here]
     <button @click="func">Click me</button> -->
  </div>
</template>

<script>
  export default {
    name: 'tabs',
    data () {
      return {
        file_paths: this.$store.state.tabs
      }
    },
    methods: {
      func () {
        console.log(this.$store.state.tabs)
      }
    }
  }
</script>

<style scoped lang="scss">
  .tabnav {
    background-color: #333;
    color: #fff;
    width: 100%;
    font-size: 1.3em;
    padding: .5em 1em;
    height: 50px;
  }

  #tab-list {
    list-style-type: none;
    margin: 0;
    padding: 0;
  }

  #tab-list li {
    display: inline;
    width: 60px;
    background-color: #595;
    margin-left: 5px;
    padding: 5px;
  }
</style>
