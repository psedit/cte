<template>
  <div id="wrapper">
    <sidebar id="sidebar" v-if="isLoggedIn"/>
    <editor id="editor" v-if="isLoggedIn"/>
    <login id="login" v-if="!isLoggedIn"/>
    <tabs id="tabs"/>
  </div>
</template>


<script>
  import Editor from './Editor'
  import Sidebar from './Sidebar'
  import Login from './Login'
  import Tabs from './Tabs/Tabs'

  import connector from '../../main/connector.js'

  export default {
    name: 'landing-page',
    computed: {
      isLoggedIn () {
        return this.$store.state.user.isLoggedIn
      }
    },
    components: { Editor, Sidebar, Login, Tabs },
    mounted () {
      const username = require('os').userInfo().username
      connector.addEventListener('open', () => {
        connector.request(
          'login-request',
          'login-response',
          {username}
        ).then(({succeed, error}) => {
          if (!succeed) {
            console.error(error)
          }
        })
      })
    },
    methods: {
      open (link) {
        this.$electron.shell.openExternal(link)
      }
    }
  }
</script>

<style scoped lang="scss">
  #wrapper {
    background:
      radial-gradient(
        ellipse at top left,
        rgba(255, 255, 255, 1) 40%,
        rgba(229, 229, 229, .9) 100%
      );

    height: 100vh;
    width: 100vw;
    display: grid;
    grid-template-areas:
        'sidebar tabs'
        'sidebar editor';
    grid-template-columns: 15em 1fr;
    grid-template-rows: auto 1fr;

    // Ensure no scroll bars on landing page
    overflow: hidden;
  }
  #sidebar {
    grid-area: sidebar;
  }
  #editor {
    grid-area: editor;
  }
  #tabs {
    grid-area: tabs;
  }
</style>
