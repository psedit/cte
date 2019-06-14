<template>
  <div class="editor">
    <code-mirror v-show="this.ready" v-model="code" ref="codemirror"/>

    <div id="placeholder" v-if="!this.ready">⇚ Select a file</div>
  </div>
</template>

<script>
  import CodeMirror from './Editor/CodeMirror'

  export default {
    name: 'Editor',

    components: {
      CodeMirror
    },
    data () {
      return {
        code: ''
      }
    },
    methods: {
      /** Updates the code that is viewed by the editor. */
      updateCode () {
        this.code = this.$store.state.fileTracker.code
      }
    },

    computed: {
      ready () {
        return this.code !== undefined && this.code !== ''
      }
    },

    mounted () {
      const cm = this.$refs.codemirror

      this.updateCode()
      this.$store.subscribe((mutation, state) => {
        if (mutation.type === 'updateCode') {
          this.updateCode()
          cm.ghostCursors.changeFilepath(this.$store.state.fileTracker.openFile)
        }
        // console.log(mutation.type)
        // console.log(mutation.payload)
      })
    }
  }
</script>

<style scoped lang="scss">
  .editor{
      width: 100%;
      height: calc(100vh - 2em);
  }

  #placeholder{
    font-size: 3em;
    height: 100%;
    width: 100%;
    line-height: 100%;
    color: #555;
    text-align: center;

    &:before {
      content: "";
      display: inline-block;
      height: 100%;
      vertical-align: middle;
    }
  }
</style>
