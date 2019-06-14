<template>
  <li class="filetreeitem" :class="{file:!isFolder, dir:isFolder}" @click="$emit('click', {name, isFolder})">
    <folder-icon v-if="isFolder"/>
    <file-icon v-else />
    <span>{{ name }}</span>
    <span v-for="user in this.activeUsers" :title="user">{{ user[0] }}</span>
    <!-- <file-tree v-if="isFolder" :file-list="children"/> -->
  </li>
</template>

<script>
  import FolderIcon from 'vue-material-design-icons/Folder'
  import FileIcon from 'vue-material-design-icons/File'
  import connector from '../../../main/connector'
  // import FileTree from './FileTree'

  export default {
    name: 'FileTreeItem',
    components: {
      FolderIcon,
      FileIcon
      // FileTree: () => import('./FileTree.vue')
    },
    props: {
      item: [Array, String],
      curPath: Array
    },
    data () {
      return {
        isOpen: false,
        activeUsers: []
      }
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

    watch: {
      item () {
        this.loadUsers()
      }
      // curPath () {
      //   this.loadUsers()
      // }
    },

    mounted () {
      if (!this.isFolder) {
        this.loadUsers()
      }
    },
    methods: {
      loadUsers () {
        const path = `./${[...this.curPath, this.item].join('/')}`
        console.log(path)
        connector.request(
          'cursor-list-request',
          'cursor-list-response',
          { file_path: path }
        ).then((response) => {
          console.log(response)
          this.activeUsers = response.cursor_list.map(cursor => cursor[0])
        })
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
