<template>
  <div id="wrapper">
    <tabs id="tabs"/>
    <sidebar id="sidebar"/>
    <editor id="editor"/>
    <error-messenger id="error-messenger"/>
  </div>
</template>


<script>
  import Editor from './Editor'
  import Sidebar from './Sidebar'
  import Tabs from './Tabs/Tabs'
  import ErrorMessenger from './ErrorMessenger'
  import connector from '../../main/connector.js'

  export default {
    name: 'landing-page',
    components: { Editor, Sidebar, Tabs, ErrorMessenger },
    mounted () {
      const username = require('os').userInfo().username
      connector.addEventListener('open', () => {
        connector.request(
          'login-request',
          'login-response',
          {username}
        ).then(({succeed, new_username: newUsername}) => {
          if (!succeed) {
            // FIXME: do error screeen pls
            console.error('hier graag')
          } else {
            this.$store.commit('changeUsername', newUsername)
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
