<template>
  <div id="error"></div>
</template>

<script>
  import connector from '../../main/connector'

  export default {
    name: 'error-messenger',
    mounted () {
      connector.addEventListener('open', () => {
        /* Start listening to error messages and show a pop up with the message
         * when receiving an error.
         */
        connector.listenToMsg('error-response', ({content}) => {
          if (content.error_code === 2) return
          if (content.error_code === 5) {
            this.$toasted.error('Someone else locked this region')
            return
          }
          let message = `Error: ${content.message}\n\nError code: ${content.error_code}`
          this.$toasted.error('Oops! We messed up...', message)
        })
      })
    }
  }
</script>

<style>
  
</style>

