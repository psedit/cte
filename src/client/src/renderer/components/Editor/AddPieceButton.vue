<template>
  <div class="add-piece-button" @click="click">
    <div class="add-piece-button-icon">
      <lock-plus-icon/>
    </div>
  </div>
</template>

<script>
  import LockPlusIcon from 'vue-material-design-icons/LockPlus'
  import Connector from './../../../../src/main/connector'
  /**
   * Displays a list of all files, i.e., the file tree, as seen on the sidebar.
   * Also manages everything relevant to the file tree.
   *
   * @module AddPieceButton
   *
   * @vue-prop {String} [pieceID=''] - The piece ID this button appends a piece to. Can be empty if you want to prepend
   *                                   a piece to the entire document.
   */

  export default {
    name: 'AddPieceButton',
    components: {
      LockPlusIcon
    },
    props: {
      pieceID: {
        type: String,
        default: ''
      }
    },
    methods: {
      /**
       * Sends a request to the server.
       */
      click () {
        Connector.send('file-lock-insert-request', {
          file_path: this.$store.state.fileTracker.openFile,
          piece_uuid: this.pieceID
        })
      }
    }
  }
</script>

<style scoped lang="scss">
.lightTheme .add-piece-button {
  --background-color: #333;
  color: #fff;
}

.add-piece-button {
  --background-color: #fff;
  $height: 1.2em;
  position: absolute;
  height: $height;
  bottom: -$height/2;
  left: 0.8em;
  z-index: 10;
  opacity: 0;
  cursor: pointer;

  &-top {
    margin-left: 0.8em;
    bottom: unset;
    left: unset;
    &:before {
      border-bottom: solid $height transparent !important;
      border-left: solid 0 transparent !important;
      border-right: solid $height/2 var(--background-color) !important;
      border-top: solid 0 transparent !important;
      /*border-color: transparent #fff transparent transparent;*/
    }
  }

  &:hover {
    opacity: 1;
  }

  /* Triangle before */
  &:before {
    content: '';
    display: inline-block;
    width: 0;
    height: 0;
    border-top: $height/2 solid transparent;
    border-bottom: $height/2 solid transparent;

    border-right: .6em solid var(--background-color);
  }
  &:after {
    content: '';
    display: block;
    position: absolute;
    top: 0;
    /*background-color: #000066;*/
    width: 2em;
    height: 1.2em;
  }

  &-icon {
    background-color: var(--background-color);
    height: $height;
    display: inline-block;
    /*padding: .1em;*/
    border-radius: 0 0.2em 0.2em 0;
    overflow: hidden;
  }
}
</style>
