<template>
  <div class="ghost-cursors">
    <ghost-cursor v-for="(cursor, index) in cursors"
                 :filepath="cursor.filepath"
                 :username="cursor.username"
                 :line="cursor.line"
                 :ch="cursor.ch"
                 :backgroundColor="cursor.color"
                 :cminstance="cm"
                 :key="index"
    />
  </div>
</template>

<script>
  import GhostCursor from './GhostCursor'

  export default {
    name: 'GhostCursors',
    components: {
      GhostCursor
    },
    props: ['piece'],

    data () {
      return {
        cm: null
      }
    },
    computed: {
      cursors () {
        return this.$store.state.user.cursors.filter(({pieceID}) => pieceID === this.piece.pieceID)
      }
    },
    methods: {
      init (cm, piece) {
        this.cm = cm
      }
    }
  }
</script>

<style scoped>
  .ghost-cursors {
    position: relative;
    top: 0;
    z-index: 4;
  }
</style>
