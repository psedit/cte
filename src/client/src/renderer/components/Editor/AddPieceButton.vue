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
.add-piece-button {
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
      border-right: solid $height/2 #fff !important;
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

    border-right: .6em solid #fff;
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
    background-color: #fff;
    height: $height;
    display: inline-block;
    /*padding: .1em;*/
    border-radius: 0 0.2em 0.2em 0;
    overflow: hidden;
  }
}
</style>
