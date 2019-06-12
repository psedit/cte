<template>
  <div class="editor">
    <code-mirror v-show="this.ready" v-model="code" ref="codemirror"/>

    <div id="placeholder" v-if="!this.ready">
      ⇚ Select a file
    </div>
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
          cm.ghostCursors.changeFilepath('test.txt')
        }
        // console.log(mutation.type)
        // console.log(mutation.payload)
      })
    }
  }
</script>

<style scoped>
  .editor{
      width: 100%;
      height: calc(100vh - 50px);
  }

  #placeholder{
    font-size: 3em;
    height: 100vh;
    width: 100vh;
    line-height: 100vh;
    color: #555;
    text-align: center;
  }
</style>
