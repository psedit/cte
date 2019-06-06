<template>
  <div id="wrapper">
    <sidebar id="sidebar"/>
    <editor id="editor"/>
  </div>
</template>


<script>
  import Editor from './Editor'
  import Sidebar from './Sidebar'

  export default {
    name: 'landing-page',
    components: { Editor, Sidebar },
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
    grid-template-areas: 'sidebar editor';
    grid-template-columns: 15em 1fr;
    grid-template-rows: 1fr;
  }

  #sidebar {
    grid-area: sidebar;
  }

  #editor {
    grid-area: editor;
  }
</style>
