<template>
    <div class="editor">
        <code-mirror ref="codemirror" v-model="code"/>
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
        code: `const a = 10
const b = 5
let c = a + b
for(let i = 0; i < c; i++) {
    c -= i;
}

console.log(c)
`
      }
    },
    methods: {
      startFakeMovement () {
        const cm = this.$refs.codemirror
        const timeout = (func) => setTimeout(func, 1000)
        function step1 () {
          cm.updateShadowCursorLocation(0, 1, 2)
          timeout(step2)
        }
        function step2 () {
          cm.updateShadowCursorLocation(0, 1, 3)
          timeout(step3)
        }
        function step3 () {
          cm.updateShadowCursorLocation(0, 3, 2)
          timeout(step4)
        }
        function step4 () {
          cm.updateShadowCursorLocation(0, 3, 4)
          timeout(step1)
        }

        setTimeout(step1, 1000)
      }
    },
    computed: {

    },

    mounted () {
      // Add fake demo cursor
      const cm = this.$refs.codemirror
      cm.addShadowCursor(1, 3, 'Martijn')
      cm.addShadowCursor(4, 3, 'Mund')
      cm.addShadowCursor(0, 3, 'Mark')
      cm.addShadowCursor(6, 3, 'HAL_9000')
      this.startFakeMovement()

      // cm.lock(3, 5)
    }
  }
</script>

<style scoped>
    .editor{
        width: 100%;
        height: 100%;
    }
</style>
