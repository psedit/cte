<template>
  <ul class="fileTree">
    <file-tree-item v-for="(item, index) in fileList" :item="item" :key="index" @click="fileClick"/>
  </ul>
</template>

<script>
  import FolderIcon from 'vue-material-design-icons/Folder'
  import FileIcon from 'vue-material-design-icons/File'
  import FileTreeItem from './FileTreeItem'

  export default {
    name: 'FileTree',
    components: {
      FolderIcon,
      FileIcon,
      FileTreeItem
    },
    props: {
      fileList: Array,
      startOpen: {
        type: Boolean,
        default: false
      }
    },
    computed: {
    },
    data () {
      return {
        isOpen: this.startOpen
      }
    },
    methods: {
      /**
       * When user clicks on file, either emit openFolder or openFile.
       *
       * @param {Object} data object consisting of name and isFolder boolean
       */
      fileClick (data) {
        if (data.isFolder) {
          this.$emit('openFolder', data.name)
        } else {
          this.$emit('openFile', data.name)
        }
      },
      isFolder (item) {
        return item instanceof Array
      },

      name (item) {
        if (this.isFolder(item)) {
          return item[0]
        } else {
          return item
        }
      },

      children (item) {
        return item[1]
      }
    }
  }
</script>

<style scoped>
  .fileTree {
    color: white;
  }
</style>
