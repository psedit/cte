import Vue from 'vue'
import axios from 'axios'

import App from './App'
import router from './router'
import store from './store'

import 'vue-material-design-icons/styles.css'
import connector from '../main/connector'
if (!process.env.IS_WEB) Vue.use(require('vue-electron'))
Vue.http = Vue.prototype.$http = axios
Vue.config.devtools = true
Vue.config.productionTip = false

/* Connect to different server.
 * Is called from index.js
 */
require('electron').ipcRenderer.on('changeURL', (event, message) => {
  Vue.toasted.show(message.toast)
  connector.reload(message.url)
  /* Join the new server
   */
  connector.addEventListener('open', () => {})
  /* Remove all tabs
   */
  store.dispatch('serverURLChange')
})

/* Show a toast message. Called from index.js. */
require('electron').ipcRenderer.on('showWorkspaceToast', (event, message) => {
  Vue.toasted.show(message)
})

/* eslint-disable no-new */
new Vue({
  components: { App },
  router,
  store,
  template: '<App/>'
}).$mount('#app')
