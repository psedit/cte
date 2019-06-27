<template>
  <div class="sidenav">
    <div id="toolbar">
      <span class="curr-folder" :title="`./${this.currPath.join('/')}`">./{{this.displayPath}}</span>
      <back-icon title="Go to previous folder" class="button" @click="previous"/>
      <home-icon title="Go to home folder" class="button" @click="home"/>
    </div>
    <div class="file-tools">
      <file-plus title="Add new file/directory" class="button" @click="createItem"/>
      <content-save title="Save current file" class="button" @click="saveFile"/>
      <cloud-download-outline title="Download project" class="button" @click="downloadProject"/>
      <upload title="Upload directory" class="button" @click="uploadDir"/>
      <file-upload title="Upload file" class="button" @click="uploadFile"/>
    </div>


    <file-tree id="file-list" :file-list="currItems" @openFolder="openFolder" @openFile="openFile"
      @renameItem="renameItem" @relocate="relocate" @removeItem="removeItem" @download="downloadFile"/>
  </div>
</template>

<script>
  import HomeIcon from 'vue-material-design-icons/Home'
  import BackIcon from 'vue-material-design-icons/ArrowLeft'
  import FilePlus from 'vue-material-design-icons/FilePlus'
  import FileUpload from 'vue-material-design-icons/FileUpload'
  import ContentSave from 'vue-material-design-icons/ContentSave'
  import CloudDownloadOutline from 'vue-material-design-icons/CloudDownloadOutline'
  import Upload from 'vue-material-design-icons/Upload'
  import connector from '../../main/connector'
  import FileTree from './Sidebar/FileTree'
  import * as fileManager from './Sidebar/fileManager'
  import * as optionParser from '../../main/optionParser'
  import {convertToJS, stitch} from '../../main/pieceTable'
  const {dialog} = require('electron').remote
  const dialogs = require('dialogs')
  const tar = require('tar')
  const fs = require('fs')
  const path = require('path')

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
      FilePlus,
      Upload,
      FileUpload,
      ContentSave,
      CloudDownloadOutline
    },
    computed: {
      /**
       *  Use completeTree to get all items in the current folder.
       */
      currItems () {
        /* When the sidebar is empty, show user a message that connection
         * with the server is being established.
         */
        if (this.completeTree.length === 0) {
          this.$toasted.show(`Getting file tree from server...`)
        }

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

        /* Sort the items alphabetically, but with all folders on top and all
         * other files below. */
        items.sort(function (a, b) {
          if (a instanceof Array && !(b instanceof Array)) {
            return -1
          } else if (!(a instanceof Array) && b instanceof Array) {
            return 1
          }
          return a > b
        })

        return items
      },

      /**
       * Return the current path string.
       */
      currPathString () {
        /* The path string has to and on a '/' so we can append a file
         * name directly to when we want the path of that file. */
        let pathString = `./${this.currPath.join('/')}`
        if (pathString.slice(-1) !== '/') {
          pathString += '/'
        }

        return pathString
      },

      /**
       * Return the path string that will be displayed at top of the sidebar.
       * There is a maximum length, to avoid style problems.
       */
      displayPath () {
        let path = this.currPath.join('/')
        if (path.length > 13) {
          return path.substr(0, 4) + '...' + path.substr(path.length - 8, path.length)
        }

        return path
      }
    },
    methods: {
      /**
       * Save current open file.
       */
      saveFile () {
        let openFilePath = this.$store.state.fileTracker.openFile
        if (openFilePath === undefined || openFilePath === '') {
          this.$toasted.show(`There was no open file. Open a file to save it.`)
          return
        }
        connector.send('file-save', {
          file_path: openFilePath
        })
      },

      /**
       * Save project to disk.
       *
       * @param {string} dataBase64 base64 encoded string with binary data of project as tar file.
       * @param {string} localPath path to local directory where project is downloaded.
       */
      saveToDisk (dataBase64, localPath) {
        /* Decode base64 to binary and make a tar file of the tar string in
         * localPath.
         */
        let buff = Buffer.from(dataBase64, 'base64')
        let filePath = `${localPath}/.project.tar`
        fs.writeFileSync(filePath, buff)

        /* Unpack tar file. */
        tar.x(
          {
            file: filePath,
            cwd: localPath,
            strip: 1
          }
        ).then(_ => {
          /* Delete tar file. */
          fs.unlinkSync(filePath)
          this.$toasted.show(`Project succesfully downloaded to ${localPath}`)
        })
      },

      /**
       * Do a file-project-request to  save the project to localDirPath.
       *
       * @param {string} localDirPath path to local working space
       */
      requestProject (localDirPath) {
        /* Get base64 encoded string with binary data of project
         * as tar file from server.
         */
        connector.request(
          'file-project-request',
          'file-project-response',
          {}
        ).then((response) => {
          this.saveToDisk(response.data, localDirPath)
        })
      },

      /**
       * Download entire project to local directory.
       */
      downloadProject () {
        let currSettings = optionParser.getSettings()
        let localDirPath = currSettings.workingPath

        /* Options for message box. */
        const options = {
          type: 'question',
          buttons: ['Cancel', 'Choose Workspace'],
          defaultId: 1,
          title: 'Local workspace not found',
          message: 'There is no local workspace specified yet.',
          detail: 'Choose a local directory in which to save the project'
        }

        /* If user has not set a local workspace (or has set a non-existing one),
         * ask for one and save the choice in the json file.
         */
        if (localDirPath === '' || (!fs.existsSync(localDirPath))) {
          dialog.showMessageBox(null, options, (response) => {
            /* If user clicks cancel, do nothing. */
            if (response === 0) return

            localDirPath = dialog.showOpenDialog({ properties: ['openDirectory'] })

            /* If user clicks cancel, do nothing. */
            if (localDirPath === undefined || localDirPath[0].toString() === '') {
              return
            }

            localDirPath = localDirPath[0].toString()
            optionParser.setLocalWorkspace(localDirPath)
            this.$toasted.show(`Succesfully set ${localDirPath} as local workspace`)
          })
          return
        }

        this.$toasted.show(`Downloading project to ${localDirPath} (this may take upto 30 seconds)`)
        this.requestProject(localDirPath)
      },

      /**
       * Gives the file path of an item. If directory, it needs
       * to end on a '/'.
       *
       * @param {object} item file or directory (members: name, isFolder)
       * @return {string} file path to current file or directory
       */
      getFilePath (item) {
        /* If item is a directory, add a '/'. */
        let filePath = `${this.currPathString}${item.name}`
        filePath = item.isFolder ? filePath + '/' : filePath

        return filePath
      },

      /**
       * When clicking on a folder, push the folder name to currPath.
       *
       * @param {string} name name of folder that is clicked on
       */
      openFolder (name) {
        this.currPath.push(name)
      },

      /**
       * Lets the user select a local map and a file on the server.
       * The user then downloads the file.
       *
       * @param {object} item file or directory that will be downloaded
       */
      downloadFile (item) {
        let filePath = this.getFilePath(item)

        /* Download the file by selecting a local file and putting the content
         * of the server file in it.
         */
        if (filePath === undefined) {
          return
        }

        /* Select a local file. */
        let options = {
          title: 'Download location',
          message: 'Select where to download file',
          defaultPath: item.name
        }

        dialog.showSaveDialog(null, options, (downloadPath) => {
          if (downloadPath === undefined) {
            return
          }

          /* Join the file. */
          connector.send(
            'file-join',
            {
              'file_path': filePath
            }
          )

          /* Get the file from. */
          connector.request(
            'file-content-request',
            'file-content-response',
            {
              'file_path': filePath,
              'start': 0,
              'length': -1
            }
          ).then((data) => {
            let fileContent = stitch(convertToJS(data)).join('')
            fs.writeFile(downloadPath, fileContent, (err) => {
              if (err) {
                dialog.showErrorBox('error', err)
                return
              }
              this.$toasted.show(`Downloaded ${filePath} to ${downloadPath}`)
            })
          })
        })
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
       *
       * @param {object} item file or directory that will be renamed
       */
      renameItem (item) {
        let oldName = item.name

        /* Define a function to change name. Assure that a file gets
         * changed into a file and a directory into a directory.
         */
        let changeName = (newName) => {
          if (newName === '' || newName === undefined) {
            return
          }

          /* If oldName is a directory, add a '/' to the new name.
           * If not, but newName is a directory, throw an error.
           */
          if (oldName.slice(-1) === '/') {
            newName = newName.slice(-1) !== '/' ? newName + '/' : newName
          } else if (newName.slice(-1) === '/') {
            dialog.showErrorBox('Renaming error', 'A file cannot be changed into a directory!')
            return
          }

          fileManager.nameChange(this.currPathString, oldName, newName)

          /* Functions in the store can only take one argument, so we have to
           * pass arguments like this. */
          let payload = {pathToDir: this.currPathString, oldName: oldName, newName: newName}
          this.$store.commit('renameTab', payload)
        }

        this.promptBox('Enter new name', oldName, changeName)
      },

      /**
       * Change location of file or directory.
       *
       * @param {object} item file or directory that will be relocated
       */
      relocate (item) {
        let filePath = this.getFilePath(item)

        this.promptBox('Enter new path', filePath, (response) => {
          if (response === undefined || response === '') {
            return
          }

          fileManager.locationChange(filePath, response)
        })
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
            case 'all':
              return true
            default:
              return true
          }
        }

        let filterItems = items.filter(filterFunc)
        filterItems = filterItems.map((item) => {
          if (item instanceof Array) {
            return item[0] + '/'
          } else {
            return item
          }
        })

        /* Add a cancel button. */
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
            dialog.showErrorBox('Reading error', err)
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
        let folderPath = localPath.split(path.split)
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
            dialog.showErrorBox('Reading error', err)
            return
          }

          /* Get dir name from newDirLocal. */
          let folderPath = newDirLocal.split(path.sep)
          let newDirName = folderPath[folderPath.length - 1]

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

          /* End recursion. */
          if (dirs === []) {
            return
          }

          /* Recursively add subdirectories. */
          dirs.forEach(dirPath => {
            this.uploadDirRecursive(dirPath, currServerPath + newDirName + '/')
          })
        })
      },

      /**
       * Upload new directory to server.
       */
      uploadDir () {
        let localDirPath = dialog.showOpenDialog({ properties: ['openDirectory'] })

        if (localDirPath === undefined || localDirPath[0].toString() === '') {
          return
        } else {
          localDirPath = localDirPath[0].toString()
        }

        /* Recursively upload folder (and all its subfolders). */
        this.uploadDirRecursive(localDirPath, this.currPathString)
      },

      /**
       * Ask user for a name and create a new file with that name.
       * If file already exists, it will be overwritten.
       */
      createItem () {
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
       *
       * @param {object} item file or directory that will be removed
       */
      removeItem (item) {
        let filePath = this.getFilePath(item)

        /* Options for promt box. */
        let buttonOptions = ['No', 'Yes']
        let title = `Deletion confirmation`
        let message = `Are you sure you want to delete ${item.name}?`
        let detail = `This cannot be undone!`

        /* Options needed for the message box. */
        let options = {
          type: 'question',
          buttons: buttonOptions,
          defaultId: 0,
          title: title,
          message: message,
          detail: detail
        }

        /* Ask user for confirmation. */
        dialog.showMessageBox(null, options, (response) => {
          /* When user selects 'No', do nothing. Otherwise remove item. */
          if (response !== 0) {
            fileManager.removeItem(filePath)
            this.$store.dispatch('removeTabByPath', filePath)
          }
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
       * Listen to file save broadcasts and display a toast indicating the saved
       * file and the user that saved it.
       */
      listenToFileSave () {
        /* Listen to file-save-broadcast messages and show a toast with the
         * file_path and username of the save.
         */
        let listen = () => {
          connector.listenToMsg('file-save-broadcast', (response) => {
            this.$toasted.show(`Succesfully saved ${response.content.file_path} by ${response.content.username}`)
          })
        }

        /* If connection is not open, first open the websocket. */
        if (connector.isOpen()) {
          listen()
        } else {
          connector.addEventListener('open', () => {
            listen()
          })
        }
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
      this.listenToFileSave()

      /* When the server URL is changes,
       * reset the directory tracker.
       */
      this.$store.subscribe((mutation, state) => {
        if (mutation.type === 'serverURLChange') {
          connector.waitUntillOpen(() => {
            this.home()
          })
          this.$toasted.show(`Connecting to server...`)
        }
      })

      /* Save file is ctrl + s (or cmd + s on mac) is pressed. */
      addEventListener('keydown', (event) => {
        /* When user has a Mac, check for command + s. */
        if (navigator.platform.indexOf('Mac') > -1) {
          if (event.metaKey && event.key === 's') this.saveFile()
        } else if (event.ctrlKey && event.key === 's') {
          this.saveFile()
        }
      })
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
