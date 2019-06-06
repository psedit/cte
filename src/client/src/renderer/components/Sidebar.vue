<template>
    <div class="sidenav">
        <ul>
            <li class="curr-folder">
                {{this.currFolder}}
            </li>
            <li v-for="file in files" >
                <a :class="file.type" v-on:click="fileClick(file)">{{file.name}}</a>
            </li>
        </ul>
    </div>
</template>

<script>
  export default {
    name: 'sidebar',
    data () {
      return {
        currFolder: './'
      }
    },
    components: { },
    computed: {
      files () {
        /* Create list of all files in current folder. */
        const fs = require('fs')
        const currFolder = this.currFolder
        let parentFolder

        /* Get path of parent folder, used for the back button. */
        if (currFolder === './') {
          parentFolder = './'
        } else {
          let currTrimmed = currFolder.slice(0, -1)
          let lastIndex = currTrimmed.lastIndexOf('/')
          parentFolder = currFolder.substring(0, lastIndex + 1)
        }

        let files = [{name: '\ud83d\udd19', type: 'dir', path: parentFolder},
          {name: 'HOME', type: 'dir', path: `./`}]

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
      fileClick (file) {
        if (file.type === 'dir') {
          this.currFolder = file.path
        } else {
          const store = this.$store
          const fs = require('fs')

          console.log('test1!!!!!')
          fs.readFile(file.path.substring(0, file.path.length - 1), 'utf8', (err, data) => {
            console.log('EINDELIJK')
            if (err) {
              throw err
            }
            console.log('NIEUWE CODE LALALA: ' + data)
            store.dispatch('updateCodeAction', data)
          })
          console.log('test2!!!!!')
          // const file = ev.target.files[0]
          // const reader = new FileReader()
          // reader.readAsText(file)
        }
      }
    }
  }
</script>

<style scoped>

  .dir {
    color: #0ff !important;
  }
  .dir:hover {
    color: rgb(12, 52, 184) !important;
    cursor:pointer;
  }

  .file {
    color: #f3f !important;
  }
  .file:hover {
    color: rgb(102, 15, 102) !important;
    cursor:pointer;
  }

  .curr-folder {
    color: #fff;
  }


  body { font-family: 'Source Sans Pro', sans-serif; }

  #wrapper {
    background:
      radial-gradient(
        ellipse at top left,
        rgba(255, 255, 255, 1) 40%,
        rgba(229, 229, 229, .9) 100%
      );
    height: 100vh;
    padding: 60px 80px;
    width: 100vw;
  }

  #logo {
    height: auto;
    margin-bottom: 20px;
    width: 420px;
  }

  main {
    display: flex;
    justify-content: space-between;
  }

  main > div { flex-basis: 50%; }

  .left-side {
    display: flex;
    flex-direction: column;
  }

  .right-side {
    float: left;
    /* This marigin has to be the same percentage as the width of the sidenav. */
    margin-left: 30%;
  }

  .sidenav {
    height: 100%;
    width: 30%;
    float:left;
    position: fixed;
    
    /* Sidebar starts at top left of screen. */
    top: 0;
    left: 0;
    
    background-color: #111;
    /* overflow-x: hidden; */
    padding-top: 20px;
    display: flex;
    overflow-y: scroll;
  }

  .sidenav a {
    padding: 6px 8px 6px 16px;
    text-decoration: none; /* No underline in links. */
    font-size: 25px;
    color: #818181;
    display: block;
  }

  .sidenav a:hover {
    color: #f1f1f1;
  }

  .welcome {
    color: #555;
    font-size: 23px;
    margin-bottom: 10px;
  }

  .title {
    color: #2c3e50;
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 6px;
  }

  .title.alt {
    font-size: 18px;
    margin-bottom: 10px;
  }

  .doc p {
    color: black;
    margin-bottom: 10px;
  }

  .doc button {
    font-size: .8em;
    cursor: pointer;
    outline: none;
    padding: 0.75em 2em;
    border-radius: 2em;
    display: inline-block;
    color: #fff;
    background-color: #4fc08d;
    transition: all 0.15s ease;
    box-sizing: border-box;
    border: 1px solid #4fc08d;
  }

  .doc button.alt {
    color: #42b983;
    background-color: transparent;
  }

  .main-textbox {
    width: 85%;
    height: 100%;
  }
</style>
