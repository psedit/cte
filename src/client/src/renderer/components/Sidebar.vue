<template>
  <div class="sidenav">
    <div id="toolbar">
      <span class="curr-folder">./{{this.currPath.join('/')}}</span>
      <back-icon title="Go to previous folder" class="button" @click="previous"/>
      <home-icon title="Go to home folder" class="button" @click="home"/>
    </div>


    <file-tree id="file-list" :file-list="currItems" @openFolder="openFolder" @openFile="openFile"/>
  </div>
</template>

<script>
  import HomeIcon from 'vue-material-design-icons/Home'
  import BackIcon from 'vue-material-design-icons/ArrowLeft'
  import connector from '../../main/connector'
  import FileTree from './Sidebar/FileTree'

  export default {
    name: 'sidebar',
    data () {
      return {
        currPath: [],
        completeTree: []
      }
    },
    components: {
      FileTree,
      HomeIcon,
      BackIcon
    },
    computed: {
      /**
       *  Use completeTree to get all items in the current folder.
       */
      currItems () {
        let items = this.completeTree

        /* For all folders in the current path (meaning, all parents)
         * search for the corresponding element in the completeTree and
         * save the content of the corrseponding file.
         */
        for (const folder of this.currPath) {
          for (const item of items) {
            if (!(item instanceof Array)) {
              continue
            }

            if (folder === item[0]) {
              items = item[1]
              break
            }
          }
        }
        return items
      }
    },
    methods: {
      /**
       * When clicking on a folder, push the folder name to currPath.
       *
       * @param {string} name name of folder that is clicked on
       */
      openFolder (name) {
        this.currPath.push(name)
      },
      /**
       * When clicking on a file, open file in editor.
       *
       * @param {string} name name of folder that is clicked on
       */
      openFile (name) {
        let filePath = `./${[...this.currPath, name].join('/')}`
        console.log(filePath)
        this.$store.dispatch('openFile', filePath)
      },
      /** When clicking on a file, go inside directory or
       *  render file and show its content on screen. */
      previous () {
        this.currPath.pop()
      },
      /** Go to the root directory. */
      home () {
        this.currPath = []
      },
      /**
        * Updates the file tree by requesting file from server.
        */
      updateFileTree () {
        connector.request(
          'file-list-request',
          'file-list-response',
          {}
        ).then((content) => {
          // this.$store.dispatch('updateFiles', content.root_tree)
          console.log('Receiving root_tree: ', content.root_tree)
          // TODO: Eventueel nog ergens anders naar fileTracker luisteren.
          this.completeTree = content.root_tree.slice()
          console.log(this.completeTree + ' in updateFileTree()')
        })
      },
      /** Open a new web socket en update the file tree. */
      openSocketUpdateTree () {
        /* When there is a change in the file structure,
        * update the file tree.
        */
        connector.listenToMsg('file-change-broadcast', (content) => {
          this.updateFileTree()
        })
        connector.addEventListener('open', () => {
          this.updateFileTree()
        })
      },
      /** When clicking on a file, show the content of the directory or
       *  open the file in the editor. If the clicked file is a directory,
       *  then also update currFiles.
       *
       *  @param {Object} file - object with members name, type (dir or file) and path.
       */
      fileClick (file) {
        if (file.type === 'dir') {
          let currFiles = this.currFiles
          this.currFolder = file.path

          /* Search for the directory that is clicked on, and update
           * currFiles to be the list of files inside that directory.
           */
          let currFilesLength = currFiles[1].length
          for (let i = 0; i < currFilesLength; i++) {
            let files = currFiles[1][i]

            /* Extract file name from the file path. */
            let fileTrimmed = file.path.slice(0, -1)
            let lastIndex = fileTrimmed.lastIndexOf('/')
            let fileName = fileTrimmed.substring(lastIndex + 1, fileTrimmed.length)

            /* Check if currFile is a directory and has the same name as
             * file that is clicked on.
             */
            if (typeof (files) !== 'string' && files[0] === fileName) {
              this.currFiles = files
              break
            }
          }
        } else {
          const filePath = file.path.substring(0, file.path.length - 1)
          this.$store.dispatch('openFile', filePath)
        }
      }
    },
    mounted () {
      this.openSocketUpdateTree()
    }
  }
</script>

<style scoped lang="scss">
  $padding: 1em;
  .sidenav {
    background-color: #111;
    display: grid;
    grid-template-rows: auto 1fr;
    height: 100%;
    border-right: 1px solid #000;
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
