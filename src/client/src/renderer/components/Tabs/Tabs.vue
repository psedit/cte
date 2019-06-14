<template>
  <div>
    <ul id="tab-list" @wheel="scroll()">
      <li v-for="tab in tabs" class="tab" @click.self="tabClick(tab.filePath)" :class="{ 'active': isActive(tab.filePath) }">
        <span>{{ tab.fileName }}</span> <close-icon class="close-tab" @click="tabRemove(tab)"/>
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
    display: inline-grid;
    grid-template-columns: 1fr auto;
    grid-column-gap: 1em;
    color: white;
    text-align: center;
    border-right: 1px solid #000;
    padding: 0 1em;
    text-decoration: none;
    height: 100%;
    font-size: 0.8em;
    line-height: 2.5em;
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
