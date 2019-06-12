<template>
  <div>
    <ul id="tab-list" @wheel="scroll()">
      <li v-for="file in filePaths" class="tab" @click="tabClick(file)">
        {{ file }}
      </li>
    </ul>
  </div>
</template>

<script>
  export default {
    name: 'tabs',
    data () {
      return {
        current_file: 'package.json'
      }
    },
    computed: {
      filePaths () {
        return this.$store.state.fileTracker.tabs
      }
    },
    methods: {
      scroll (e) {
        console.log('scrolling')
      },
      tabClick (file) {
        this.$store.dispatch('openFile', file)
      }
    }
  }
</script>

<style scoped lang="scss">
  ul {
    list-style-type: none;
    margin: 0;
    padding: 0;
    background-color: #333;
    color: #fff;
    width: 100%;
    font-size: 1.3em;
    height: 50px;
    white-space: nowrap;
    overflow: hidden;
  }
  li {
    float: left;
    display: inline;
    color: white;
    text-align: center;
    border-right: 1px solid #000;
    padding: 10px;
    text-decoration: none;
    height: 100%;
    min-width: 200px;
  }

  li:hover {
    background-color: #111;
  }

</style>
