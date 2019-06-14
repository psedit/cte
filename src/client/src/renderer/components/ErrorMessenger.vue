<template>
  <div class="error-messenger">
  </div>
</template>

<script>
import connector from '../../main/connector'
export default {
  name: 'error-messenger',
  methods: {

  },
  mounted () {
    console.log('Ik ben een error!!!')
    connector.addEventListener('open', () => {
    /* Start listening to error messages
     */
      connector.listenToMsg('error-response', (content) => {
        window.alert('Error: ' + content.message + '\n Error code: ' + content.error_code)
      })
    })
  }
}
</script>
