<template>
  <div class="sidenav">
    <div id="toolbar">
      <span class="curr-folder">./{{this.currPath.join('/')}}</span>
      <back-icon title="Go to previous folder" class="button" @click="previous"/>
      <home-icon title="Go to home folder" class="button" @click="home"/>
    </div>
    <div class="file-tools">
      <upload title="Upload directory" class="button" @click="uploadDir"/>
      <file-upload title="Upload file" class="button" @click="uploadFile"/>
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
  import FileUpload from 'vue-material-design-icons/FileUpload'
  import Upload from 'vue-material-design-icons/Upload'
  import connector from '../../main/connector'
  import FileTree from './Sidebar/FileTree'
  import * as fileManager from './Sidebar/fileManager'
  const { dialog } = require('electron').remote
  // const read = require('fs-readdir-recursive')
  const dialogs = require('dialogs')
  const fs = require('fs')

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
      Upload,
      FileUpload
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
       * Open a prompt box and ask user for input.
       *
       * @param {string} promptString message shown in promptBox
       * @param {string} defaultString default input for prompt
       * @param {function} callback callback function to be executed
       */
      promptBox (promptString, defaultString, callback) {
        const d = dialogs()

        d.prompt(promptString, defaultString, response => {
          callback(response)
        })
      },

      /**
       * This function checks if two paths are of the same type
       * (both directories or both files).
       *
       * @param {string} path1 first path
       * @param {string} path2 second path
       * @return {Boolean} True if paths are of the same type
       */
      sameType (path1, path2) {
        if (path1.slice(-1) === '/' && path2.slice(-1) === '/') {
          /* Both paths indicate directories. */
          return true
        } else if (path1.slice(-1) !== '/' && path2.slice(-1) !== '/') {
          /* Both paths indicate files. */
          return true
        }
        return false
      },

      /**
       * Get an array of strings of items in current directory.
       */
      itemNames () {
        let items = []

        for (let i = 0; i < this.currItems.length; i++) {
          let item = this.currItems[i]
          if (item instanceof Array) {
            items.push(`${item[0]}/`)
          } else {
            items.push(item)
          }
        }

        return items
      },

      /**
       * Change name of file or directory.
       */
      renameFile () {
        /* Let user select file or directory from current folder.
         * First get all files and directories. */
        let items = ['cancel']
        items = items.concat(this.itemNames())

        /* Options needed for the message box. */
        let options = {
          type: 'question',
          buttons: items,
          defaultId: 0,
          title: 'Rename file or directory',
          message: 'Select item to rename'
        }

        /* Let user choose which file to rename. */
        dialog.showMessageBox(null, options, (response) => {
          /* When user selects 'cancel', do nothing. */
          if (response === 0) {
            return
          }

          let oldName = items[response]

          /* Define a function to change name. Assure that a file gets
           * changed into a file and a directory into a directory.
           */
          let changeName = (newName) => {
            if (newName === '' || newName === undefined) {
              return
            }

            /* If oldName is a directory, add a '/' to the new name.
             * If not, but newName is a directory, throw an error. */
            if (oldName.slice(-1) === '/') {
              newName = newName.slice(-1) !== '/' ? newName + '/' : newName
            } else if (newName.slice(-1) === '/') {
              console.log('A file cannot be changed into a directory!')
              return
            }

            fileManager.nameChange(this.currPathString, oldName, newName)
          }

          this.promptBox('Enter new name', oldName, changeName)
        })
      },

      /**
       * Change location of file or directory.
       */
      relocateFile () {
        let selectFolder = (filePath, payload) => {
          this.promptBox('Enter path', filePath, (response) => {
            if (response === undefined || response === '') {
              return
            }
            console.log('Requesting location change: ')
            console.log('old_path: ', filePath)
            console.log('new_path: ', response)
            fileManager.locationChange(filePath, response)
          })
        }
        this.selectItem('File move', 'select a file to move', '', this.currItems, 'file', selectFolder)
      },

      /* Let the user select a file.
        * Itemtype can be:
        *  'file'
        *  'all'
        *  'dir'
        *  Passes selected filename in callback.
        *  NOTE: can return 0 in case of cancel!
        */
      selectItem (title, message, detail, items = this.currItems, itemType, callback) {
        /* Get all items of the desired type.
        */
        let filterFunc = (item) => {
          switch (itemType) {
            case 'file':
              return !(item instanceof Array)
            case 'dir':
              return (item instanceof Array)
            default:
              return true
          }
        }

        let filterItems = items.filter(filterFunc)

        /* Add a cancel button
          */
        let buttonOptions = ['cancel', ...filterItems]

        /* Options needed for the message box. */
        let options = {
          type: 'question',
          buttons: buttonOptions,
          defaultId: 0,
          title: title,
          message: message,
          detail: detail
        }
        let returnValue = 0
        /* Let user choose which file to delete. */
        dialog.showMessageBox(null, options, (response) => {
          /* When user selects 'cancel', do nothing. */
          if (response === 0) {
            return
          }
          console.log('button options', buttonOptions)
          returnValue = buttonOptions[response]
          returnValue = `${this.currPathString}${returnValue}`
          callback(returnValue)
        })
      },

      /**
       * Upload a file to server (helper function of uploadFile),
       * does the actual communication with server.
       *
       * @param {string} localPath local path to file that will be uploaded
       * @param {string} serverPath destination path on server
       *
       * @see uploadFile()
       */
      uploadFileHelper (localPath, serverPath) {
        /* Read content from file and request file upload from server. */
        fs.readFile(localPath, (err, data) => {
          if (err) {
            console.log(err)
            return
          }

          fileManager.uploadFile(serverPath, data.toString())
        })
      },

      /**
       * Upload new file to server.
       */
      uploadFile () {
        let localPath = dialog.showOpenDialog({ properties: ['openFile'] })

        if (localPath === undefined || localPath.toString() === '') {
          return
        } else {
          localPath = localPath.toString()
        }

        /* Get name of file from path. */
        let folderPath = localPath.split('/')
        let newFileName = folderPath[folderPath.length - 1]
        let serverPath = this.currPathString + newFileName

        this.uploadFileHelper(localPath, serverPath)
      },

      /**
       * Recursively upload subdirectories to server.
       *
       * @param {string} newDirLocal local path to new directory
       * @param {string} currServerPath destination path in which to make new directory
       */
      uploadDirRecursive (newDirLocal, currServerPath) {
        /* Read local directory. */
        fs.readdir(newDirLocal, {withFileTypes: true}, (err, files) => {
          if (err) {
            console.log(err)
            return
          }

          /* Get dir name from newDirLocal. */
          let folderPath = newDirLocal.split('/')
          let newDirName = folderPath[folderPath.length - 1]
          console.log('NEWDIRNAME: ' + newDirName)

          let dirs = []
          files.forEach(file => {
            let localPath = `${newDirLocal}/${file}`
            let stat = fs.statSync(localPath)

            /* Upload all files and make a list of the directories. */
            if (stat.isDirectory()) {
              dirs.push(localPath)
            } else {
              let serverPath = currServerPath + newDirName + '/' + file

              this.uploadFileHelper(localPath, serverPath)
            }
          })

          /* Recursively add subdirectories. */
          dirs.forEach(dirPath => {
            /* Get dir name from dirPath. */
            let folderPath = dirPath.split('/')
            let newSubDirName = folderPath[folderPath.length - 1]
            console.log('RECURSIVE CALL! newDirLocal: ' + dirPath + ' currServerPath: ' + currServerPath + newDirName + '/')
            this.uploadDirRecursive(dirPath, currServerPath + newDirName + '/' + newSubDirName + '/')
          })
        })
      },

      /**
       * Upload new directory to server.
       */
      uploadDir () {
        let localDirPath = dialog.showOpenDialog({ properties: ['openDirectory'] })

        if (localDirPath === undefined || localDirPath[0].toString().toString() === '') {
          return
        } else {
          localDirPath = localDirPath[0].toString().toString()
        }

        /* Recursively upload folder (and all its subfolders). */
        this.uploadDirRecursive(localDirPath, this.currPathString)
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
          if (newFileName === '' || newFileName === undefined) {
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
        this.selectItem('Delete file', 'Select file to delete', 'This cannot be undone!', this.currItems, 'all', (filePath) => {
          /* When user selects 'cancel', do nothing. */
          if (filePath === undefined) {
            return
          }
          fileManager.removeFile(filePath)
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
    grid-template-columns: 1fr auto auto auto auto auto auto;
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
