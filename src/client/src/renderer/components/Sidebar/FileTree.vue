<template>
  <div>
    <ul class="fileTree">
      <file-tree-item v-for="(item, index) in fileList" :item="item" :key="index" @click="fileClick" @rightClick="rightClick"/>
    </ul>

    <vue-simple-context-menu
      :elementId="'myUniqueIdFile'"
      :options="rightClickOptionsFile"
      :ref="'vueSimpleContextMenuFile'"
      @option-clicked="optionClicked">
    </vue-simple-context-menu>

    <vue-simple-context-menu
      :elementId="'myUniqueIdDir'"
      :options="rightClickOptionsDir"
      :ref="'vueSimpleContextMenuDir'"
      @option-clicked="optionClicked">
    </vue-simple-context-menu>
  </div>
</template>

<script>
  import FolderIcon from 'vue-material-design-icons/Folder'
  import FileIcon from 'vue-material-design-icons/File'
  import FileTreeItem from './FileTreeItem'
  import 'vue-simple-context-menu/dist/vue-simple-context-menu.css'
  import VueSimpleContextMenu from 'vue-simple-context-menu'

  /**
   * Displays a list of all files, i.e., the file tree, as seen on the sidebar.
   * Also manages everything relevant to the file tree.
   *
   * @module fileTracker
   *
   * @vue-data {Boolean} isOpen -
   * @vue-data {Object[]} rightClickOptionsFile - a list of all options for when you rightclick a file.
   * @vue-data {Object[]} rightClickOptionsDir - a list of all options for when you rightclick a directory.
   */

  export default {
    name: 'FileTree',
    components: {
      FolderIcon,
      FileIcon,
      FileTreeItem,
      VueSimpleContextMenu
    },
    props: {
      fileList: Array
    },
    mounted () {
      addEventListener('click', (e) => {
        this.$refs.vueSimpleContextMenuDir.hideContextMenu()
        this.$refs.vueSimpleContextMenuFile.hideContextMenu()
      })
    },
    data () {
      return {
        rightClickOptionsFile: [{name: 'Download'}, {name: 'Rename'}, {name: 'Relocate'}, {name: 'Delete'}],
        rightClickOptionsDir: [{name: 'Rename'}, {name: 'Relocate'}, {name: 'Delete'}]
      }
    },
    methods: {
      /**
       * When user clicks on file, either emit openFolder or openFile.
       *
       * @param {Object} file object consisting of name and isFolder boolean
       */
      fileClick (file) {
        if (file.isFolder) {
          this.$emit('openFolder', file.name)
        } else {
          this.$emit('openFile', file.name)
        }
      },

      /**
       * When right clicking on an item, show a context menu.
       *
       * @param {object} event the right click event
       * @param {object} item file or directory
       */
      rightClick (event, item) {
        this.$refs.vueSimpleContextMenuDir.hideContextMenu()
        this.$refs.vueSimpleContextMenuFile.hideContextMenu()
        if (item.isFolder) {
          this.$refs.vueSimpleContextMenuDir.showMenu(event, item)
        } else {
          this.$refs.vueSimpleContextMenuFile.showMenu(event, item)
        }
      },

      /**
       * When clicking on an option from the context menu, call the
       * appropriate function.
       *
       * @param {object} event the event object
       *                 event.option.name indicates the selected option
       *                 event.item is the item clicked on
       */
      optionClicked (event) {
        switch (event.option.name) {
          case 'Download':
            this.$emit('download', event.item)
            break
          case 'Rename':
            this.$emit('renameItem', event.item)
            break
          case 'Relocate':
            this.$emit('relocate', event.item)
            break
          case 'Delete':
            this.$emit('removeItem', event.item)
            break
        }
      }
    }
  }
</script>

<style scoped>
  .fileTree {
    color: white;
    list-style: none;
  }
</style>
