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
  import connector from 'path/to/connector'

  export default {
    name: 'sidebar',
    data () {
      return {
        /* The variable currFolder is relative to the root of the server. */
        currFolder: './',
        /* The variable currFiles contains all files in currFolder. */
        currFiles: [],
        dirTree: []
      }
    },
    components: {
      HomeIcon,
      BackIcon,
      FolderIcon,
      FileIcon
    },
    // FIXME: use the data from vuex
    computed: {
      /** Loop over all files in current directory and add
       *  object to files array, storing the name and type
       *  (either directory or file) of the file.
       */
      files () {
        // currFiles = [currFolder, [<bestanden>]]
        let files
        let currFiles = this.currFiles
        let currFolder = this.currFolder

        /*  For sorting purposes, first push all directories
         *  and then all other files.
         */
        currFiles[1].forEach(file => {
          if (typeof (file) !== 'string') {
            files.push({name: file, type: 'dir', path: `${currFolder}${file}/`})
          }
        })

        currFiles[1].forEach(file => {
          if (typeof (file) === 'string') {
            files.push({name: file, type: 'file', path: `${currFolder}${file}/`})
          }
        })

        return files
      }
    },
    methods: {
      /** Update the directory tree (by getting it from store). */
      // updateDirTree () {
      //     this.dirTree = this.$store.state.fileTracker.dirTree
      // },

      /** When clicking on a file, go inside directory or
       *  render file and show its content on screen. */
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
      /** Go to the root directory. */
      home () {
        this.fileClick({
          // name: parentFolder,
          type: 'dir',
          path: './'
        })
      },
      /** When clicking on a file, show the content of the directory or
       *  open the file in the editor. If the clicked file is a directory,
       *  then also update currFiles.
       */
      fileClick (file) {
        if (file.type === 'dir') {
          let currFiles = this.currFiles
          this.currFolder = file.path

          /*  */
          for (let i = 0; i < currFiles.length; i++) {
            let currFile = currFiles[1][i]

            /* Extract file name from the file path. */
            let lastIndex = file.path.lastIndexOf('/')
            let fileName = file.path.substring(lastIndex, -1)

            if (typeof (currFile) !== 'string' && currFile[0] === fileName) {
              this.currFiles = currFile
            }
          }
        } else {
          this.$store.dispatch('openFile', file.path)
        }
      }
    },
    mounted () {
      connector.addEventListener('open', () => {
        connector.listenToMsg('file-list-broadcast', (content) => {
          console.log(content.root_tree)
          this.$store.dispatch('updateFilesAction', content.root_tree)

          // TODO: Eventueel nog ergens anders naar fileTracker luisteren.
          this.dirTree = this.$store.state.fileTracker.dirTree
        })
      })
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
