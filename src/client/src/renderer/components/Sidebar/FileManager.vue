<template>
  <div id="fileManger">
  </div>
</template>

<script>
  import connector from '../../main/connector'
import { connect } from 'tls';

  export default {
    name: 'error-messenger',
    mounted () {
      
    },
    methods: {
      /** Sends message to the server indicating a file change.
       * 
       * @param {string} old_path empty if creating new file
       * @param {string} new_path empty if removing file
       * @param {string} file_content the content of the file 
       */
      fileChangeRequest (old_path, new_path, file_content) {
        connector.addEventListener('open', () => {
          connector.send('file-change', {
            old_path,
            new_path,
            file_content
          })
        })
      },
      /**  Create a new empty file on the server.
       * Sends a message to the server, creating a new file
       *
       * @param {string} path path of file to be created.
       */
      newFile (path) {
        this.fileChangeRequest('', path, '')
      },
      removeFile (path) {
        this.fileChangeRequest(path, '', '')
      },
      nameChange(old_path, new_path, file_content) {
        
      }
    }
  }
</script>

<style>
  
</style>

