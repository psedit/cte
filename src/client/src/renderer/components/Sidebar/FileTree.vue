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
       * @param {Object} file object consisting of name and isFolder boolean
       */
      fileClick (file) {
        if (file.isFolder) {
          this.$emit('openFolder', file.name)
        } else {
          this.$emit('openFile', file.name)
        }
      }
    }
  }
</script>

<style scoped>
  .fileTree {
    color: white;
  }
</style>
