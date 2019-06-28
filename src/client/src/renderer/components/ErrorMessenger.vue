<template>
  <div id="error"></div>
</template>

<script>
  import connector from '../../main/connector'

  export default {
    name: 'error-messenger',
    /**
     * @module ErrorMessenger
     * @desc Displays error toasts if there is an error.
     */
    mounted () {
      connector.addEventListener('open', () => {
        /* Start listening to error messages and show a pop up with the message
         * when receiving an error.
         */
        // connector.listenToMsg('error-response', ({content}) => {
        //   if (content.error_code === 2) return
        //   let message = `Error: ${content.message}\n\nError code: ${content.error_code}`
        //   dialog.showErrorBox('Oops! We messed up...', message)
        // })
      })
    }
  }
</script>

<style>

</style>

