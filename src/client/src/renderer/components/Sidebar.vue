<template>
  <div class="sidenav">
    <div id="toolbar">
      <span class="curr-folder">{{this.currFolder}}</span>
      <back-icon title="Go to previous folder" class="button" @click="previous"/>
      <home-icon title="Go to home folder" class="button" @click="home"/>
    </div>


    <ul id="file-list">
      <li v-for="file in files" :class="file.type" @click="fileClick(file)">
        <folder-icon v-if="file.type === 'dir'" />
        <file-icon v-if="file.type === 'file'" />
        {{ file.name }}
      </li>
    </ul>
  </div>
</template>

<script>
  import HomeIcon from 'vue-material-design-icons/Home'
  import BackIcon from 'vue-material-design-icons/ArrowLeft'
  import FolderIcon from 'vue-material-design-icons/Folder'
  import FileIcon from 'vue-material-design-icons/File'

  export default {
    name: 'sidebar',
    data () {
      return {
        currFolder: './'
      }
    },
    components: {
      HomeIcon,
      BackIcon,
      FolderIcon,
      FileIcon
    },
    computed: {
      files () {
        /* Create list of all files in current folder. */
        const fs = require('fs')
        const currFolder = this.currFolder

        // let files = [{name: '\ud83d\udd19', type: 'dir', path: parentFolder},
        //   {name: 'HOME', type: 'dir', path: `./`}]
        let files = []

        /* Loop over all files in current directory and add
         * object to files array, storing the name and type
         * (either directory or file) of the file.
         * For sorting purposes, first push all directories
         * and then all other files. */
        fs.readdirSync(currFolder).forEach(file => {
          if (fs.lstatSync(currFolder + file).isDirectory()) {
            files.push({name: file, type: 'dir', path: `${currFolder}${file}/`})
          }
        })

        fs.readdirSync(currFolder).forEach(file => {
          if (!fs.lstatSync(currFolder + file).isDirectory()) {
            files.push({name: file, type: 'file', path: `${currFolder}${file}/`})
          }
        })

        return files
      }
    },
    methods: {
      /* When clicking on a file, go inside directory or
       * render file and show its content on screen. */
      previous () {
        let parentFolder
        /* Get path of parent folder, used for the back button. */
        if (this.currFolder === './') {
          parentFolder = './'
        } else {
          let currTrimmed = this.currFolder.slice(0, -1)
          let lastIndex = currTrimmed.lastIndexOf('/')
          parentFolder = this.currFolder.substring(0, lastIndex + 1)
        }
        this.fileClick({
          // name: parentFolder,
          type: 'dir',
          path: parentFolder
        })
      },

      home () {
        this.fileClick({
          // name: parentFolder,
          type: 'dir',
          path: './'
        })
      },

      fileClick (file) {
        if (file.type === 'dir') {
          this.currFolder = file.path
        } else {
          this.$store.dispatch('openFile', file.path)
        }
      }
    }
  }
</script>

<style scoped lang="scss">
  $padding: 1em;

  .sidenav {
    background-color: #111;
    display: grid;
    grid-template-rows: auto 1fr;
    height: 100vh;
  }

  .curr-folder {
    color: #ccc;
    font-size: 0.8em;
  }

  #toolbar {
    background-color: #333;
    color: #fff;
    font-size: 1.3em;
    padding: .5em $padding;
    display: grid;
    grid-template-columns: 1fr auto auto;
    grid-gap: 0.5em;
    height: 50px;
  }

  #file-list {
    overflow-y: auto;
    padding: 0 1em;
    margin-top: .5em;
    list-style-type: none;
  }

  .button {
    cursor: pointer;
    :hover {
      color: #fff;
    }
  }

  .dir {
    color: #ccc;
    cursor:pointer;

    &:hover {
      color: rgb(102, 15, 102);
    }
  }

  .file {
    color: #fff;

    &:hover {
      color: rgb(102, 15, 102);
      cursor: pointer;
    }
  }


  .sidenav a {
    /*padding: 6px 8px 6px 16px;*/
    text-decoration: none; /* No underline in links. */
    font-size: 25px;
    color: #818181;
    display: block;

    &:hover {
      color: #f1f1f1;

    }
  }
</style>
