<template>
  <li class="filetreeitem" :class="{file:!isFolder, dir:isFolder}" @click="$emit('click', {name, isFolder})">
    <folder-icon v-if="isFolder"/>
    <file-icon v-else />
    <span>{{ name }}</span>
    <!-- <file-tree v-if="isFolder" :file-list="children"/> -->
  </li>
</template>

<script>
  import FolderIcon from 'vue-material-design-icons/Folder'
  import FileIcon from 'vue-material-design-icons/File'
  // import FileTree from './FileTree'

  export default {
    name: 'FileTreeItem',
    components: {
      FolderIcon,
      FileIcon
      // FileTree: () => import('./FileTree.vue')
    },
    props: {
      item: [Array, String]
    },
    data () {
      return {
        isOpen: false
      }
    },
    computed: {
      isFolder () {
        return this.item instanceof Array
      },

      name () {
        if (this.isFolder) {
          return this.item[0]
        } else {
          return this.item
        }
      },

      children () {
        if (this.isFolder) {
          return this.item[1]
        } else {
          return []
        }
      }

    },
    methods: {
    },
    mounted () {
      if (this.isFolder) {
        console.log(this.children)
      }
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
