import Vue from 'vue'
import axios from 'axios'

import App from './App'
import router from './router'
import store from './store'

import 'vue-material-design-icons/styles.css'
import connector from '../main/connector'
import * as optionParser from '../main/optionParser'

if (!process.env.IS_WEB) Vue.use(require('vue-electron'))
Vue.http = Vue.prototype.$http = axios
Vue.config.devtools = true
Vue.config.productionTip = false

/* Connect to different server.
 * Is called from index.js
 */
require('electron').ipcRenderer.on('changeURL', (event, message) => {
  /* Try connecting to the server. If given url is invalid, connect
   * to default server and reset the json file accordingly.
   */
  try {
    connector.reload(message.url)
    Vue.toasted.show(message.toast)
  } catch (err) {
    Vue.toasted.show(`Server URL ${message.url} is invalid.`)
    optionParser.resetServerURL()
    let server = optionParser.getSettings().serverURL
    connector.reload(server)
    Vue.toasted.show(`Swithcing back to ${server}`)
  }

  /* Join the new server. */
  connector.addEventListener('open', () => {})

  /* Remove all tabs. */
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
