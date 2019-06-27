<template>
  <div>
    <ul id="tab-list" @wheel="scrollTabs">
      <li v-for="tab in tabs" class="tab" @click.self="tabClick(tab.filePath)" :class="{ 'active': isActive(tab.filePath) }">
        {{ tab.fileName }} <close-icon class="close-tab" @click="tabRemove(tab)"/>
      </li>
    </ul>
  </div>
</template>

<script>
  import CloseIcon from 'vue-material-design-icons/CloseCircle'

  /**
   * Displays the tab bar and manages everything relevant to the tabs.
   *
   * @module Tabs
   *
   * @vue-computed {Array} tabs - A list of all tab objects
   * @vue-computed {String} openFile - The filepath to the file which is currently opened
   */
  export default {
    name: 'tabs',
    components: {
      CloseIcon /* The icon for closing a tab. */
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
      /**
       * Scrolls to the next tab on the tab bar, based on the given scroll event.
       * The scroll event determines in which direction you scroll the tab bar.
       * @param {Object} event the scroll event
       */
      scrollTabs (e) {
        let direction = 1
        if (e.deltaY < 0) {
          direction = 0
        }
        this.$store.dispatch('scrollTab', direction)
      },
      /**
       * Opens a file in the editor. This function is meant to be used for when
       * a given tab is clicked.
       * @param {string} filePath the file path to document to be opened
       */
      tabClick (filePath) {
        this.$store.dispatch('openFile', filePath)
      },
      /**
       * Removes a tab from the tab bar
       * @param {Object} tab the tab object that needs to be removed
       */
      tabRemove (tab) {
        this.$store.dispatch('removeTab', tab)
      },
      /* Checks if a given filePath is the currently opened path. */
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
    cursor: pointer;
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
    padding: 2px 6px;
  }

</style>
