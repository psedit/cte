<template>
  <div id="wrapper">
    <main>
      <!-- Create a sidemenu. -->
      <sidebar />
      <editor />
      

      <!-- <div class="right-side">
        <span class="title">
          Welcome to your new project!
        </span>
        <textarea name="standard-text" class="main-textbox"></textarea>
      </div> -->
    </main>
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

<style>
  @import url('https://fonts.googleapis.com/css?family=Source+Sans+Pro');

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

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
