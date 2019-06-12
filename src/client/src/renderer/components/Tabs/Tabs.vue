<template>
  <div>
    <ul id="tab-list" @wheel="scroll()">
      <li v-for="tab in tabs" class="tab" @click="tabClick(tab.filePath)" :class="{ 'active': isActive(tab.filePath) }">
        {{ tab.fileName }}
      </li>
    </ul>
  </div>
</template>

<script>
  export default {
    name: 'tabs',
    computed: {
      tabs () {
        return this.$store.state.fileTracker.tabs
      },
      openFile  () {
        return this.$store.state.fileTracker.openFile
      }
    },
    methods: {
      scroll (e) {
        console.log('scrolling')
      },
      tabClick (fileName) {
        this.$store.dispatch('openFile', fileName)
      },
      isActive (filePath) {
        return this.openFile === filePath
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

  .active {
    background-color: #111;
  }

  li:hover {
    cursor: pointer;
  }

</style>
