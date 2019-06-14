<template>
  <div>
    <ul id="tab-list" @wheel="scroll()">
      <li v-for="tab in tabs" class="tab" @click.self="tabClick(tab.filePath)" :class="{ 'active': isActive(tab.filePath) }">
        {{ tab.fileName }} <close-icon class="close-tab" @click="tabRemove(tab)"/>
      </li>
    </ul>
  </div>
</template>

<script>
  import CloseIcon from 'vue-material-design-icons/CloseCircle'
  export default {
    name: 'tabs',
    components: {
      CloseIcon
    },
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
      tabRemove (tab) {
        this.$store.dispatch('removeTab', tab)
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
    height: 2em;
    white-space: nowrap;
    overflow: hidden;
  }
  li {
    display: inline-block;
    color: white;
    text-align: center;
    border-right: 1px solid #000;
    padding: 0 2em;
    text-decoration: none;
    height: 100%;
    line-height: 2em;
    /*min-width: 200px;*/
  }

  .active {
    background-color: #777;
  }

  .close-tab {
    cursor: pointer;
    padding: 2px 6px;
  }

</style>
