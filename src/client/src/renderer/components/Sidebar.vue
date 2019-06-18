<template>
  <div class="sidenav">
    <div id="toolbar">
      <span class="curr-folder">./{{this.currPath.join('/')}}</span>
      <back-icon title="Go to previous folder" class="button" @click="previous"/>
      <home-icon title="Go to home folder" class="button" @click="home"/>
    </div>
    <div class="file-tools">
      <upload title="Upload file" class="button" @click="uploadFile"/>
      <file-plus title="Add new file" class="button" @click="createFile"/>
      <file-document-edit title="Rename file" class="button" @click="renameFile"/>
      <file-move title="Relocate file" class="button" @click="relocateFile"/>
      <file-remove title="Remove file" class="button" @click="removeFile"/>
    </div>


    <file-tree id="file-list" :file-list="currItems" @openFolder="openFolder" @openFile="openFile"/>
  </div>
</template>

<script>
  import HomeIcon from 'vue-material-design-icons/Home'
  import BackIcon from 'vue-material-design-icons/ArrowLeft'
  import FileRemove from 'vue-material-design-icons/FileRemove'
  import FilePlus from 'vue-material-design-icons/FilePlus'
  import FileDocumentEdit from 'vue-material-design-icons/FileDocumentEdit'
  import FileMove from 'vue-material-design-icons/FileMove'
  import Upload from 'vue-material-design-icons/Upload'
  import connector from '../../main/connector'
  import FileTree from './Sidebar/FileTree'
  import * as fileManager from './Sidebar/fileManager'
  const { dialog } = require('electron').remote
  const dialogs = require('dialogs')

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
      BackIcon,
      FileRemove,
      FilePlus,
      FileDocumentEdit,
      FileMove,
      Upload
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
      },

      currPathString () {
        /* The path string has to and on a '/' so we can append a file
         * name directly to when we want the path of that file. */
        let pathString = `./${this.currPath.join('/')}`
        if (pathString.slice(-1) !== '/') {
          pathString += '/'
        }

        return pathString
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
       * Change name of file or directory.
       */
      renameFile () {
        console.log('rename')
      },

      /**
       * Change location of file or directory.
       */
      relocateFile () {
        console.log('relocate')
      },

      /**
       * Upload new file to server.
       */
      uploadFile () {
        console.log('uploading')
      },

      /**
       * Ask user for a name and create a new file with that name.
       * If file already exists, it will be overwritten.
       */
      createFile () {
        const d = dialogs()

        let promptString = `Add new file or directory. Enter desired name.
        If final character is '/', a new directory will be added.
        Note: if file alread exists, it will be overwritten.`

        d.prompt(promptString, 'newFile', newFileName => {
          if (newFileName === '') {
            return
          }

          /* Add new file. */
          fileManager.newFile(`${this.currPathString}${newFileName}`)
        })
      },

      /**
       * Let user choose a file and remove that file from the server.
       */
      removeFile () {
        let items = this.currItems

        /* Get all files. */
        let files = items.filter((item) => {
          return !(item instanceof Array)
        })
        files = ['cancel', ...files]

        /* Options needed for the message box. */
        let options = {
          type: 'question',
          buttons: files,
          defaultId: 0,
          title: 'Delete file',
          message: 'Select file to delete',
          detail: 'This cannot be undone!'
        }

        /* Let user choose which file to delete. */
        dialog.showMessageBox(null, options, (response) => {
          /* When user selects 'cancel', do nothing. */
          if (response === 0) {
            return
          }

          fileManager.removeFile(`${this.currPathString}${files[response]}`)
        })
      },

      /**
       * When clicking on a file, open file in editor.
       *
       * @param {string} name name of folder that is clicked on
       */
      openFile (name) {
        let filePath = `./${[...this.currPath, name].join('/')}`
        this.$store.dispatch('openFile', filePath)
      },

      /**
       * Pop the last element from currPath.
       */
      previous () {
        this.currPath.pop()
      },

      /**
       * Empty the currPath array.
       */
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
          this.completeTree = content.root_tree.slice()
        })
      },

      /**
       * Open a new web socket and update the file tree.
       */
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
    grid-template-rows: auto auto 1fr;
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
    padding: 0 $padding;
    display: grid;
    grid-template-columns: 1fr auto auto;
    grid-gap: 0.5em;
    align-items: center;
    height: 2em;
  }
  .file-tools {
    background-color: #555;
    display: grid;
    grid-template-columns: 1fr auto auto auto auto auto;
    grid-gap: 0.5em;
    align-items: center;
    color: #fff;
    font-size: 1.3em;
    padding: 0 $padding;
    height: 2em;
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
