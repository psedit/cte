<template>
  <li class="filetreeitem" :class="{file:!isFolder, dir:isFolder}" @click="$emit('click', {name, isFolder})" @contextmenu.prevent.stop="$emit('rightClick', $event, {name, isFolder})" >
    <folder-icon v-if="isFolder"/>
    <file-icon v-else />
    <span>{{ name }}</span>
    <!-- <file-tree v-if="isFolder" :file-list="children"/> -->
  </li>
</template>

<script>
  /**
   * @module FileTreeItem
   * @desc handles an invdidual folder or link
   * @vue-prop {Array} item contains the file tree of that item.
   */
  import FolderIcon from 'vue-material-design-icons/Folder'
  import FileIcon from 'vue-material-design-icons/File'

  export default {
    name: 'FileTreeItem',
    components: {
      FolderIcon,
      FileIcon
    },
    props: {
      item: [Array, String]
    },
    computed: {
      /**
       * Check if item is a folder.
       */
      isFolder () {
        return this.item instanceof Array
      },

      /**
       * Get the name of an item (file or directory).
       */
      name () {
        if (this.isFolder) {
          return this.item[0]
        } else {
          return this.item
        }
      },

      /**
       * Get the children of a folder.
       */
      children () {
        if (this.isFolder) {
          return this.item[1]
        } else {
          return []
        }
      }

    },
    methods: {
    }
  }
</script>

<style lang="scss" scoped>
.filetreeitem {
  cursor:pointer;
  &:hover{
    color: #0E4
  }
}
</style>
