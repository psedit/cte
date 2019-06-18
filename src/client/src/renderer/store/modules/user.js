const state = {
  username: '',
  isLoggedIn: false
}

const mutations = {
  changeUsername (state, username) {
    state.username = username
  },
  updateLogin (state, value) {
    state.isLoggedIn = value
  }
}

const actions = {
  login (state, username) {
    state.commit('changeUsername', username)
    state.commit('updateLogin', true)
  }
}

export default {
  state,
  mutations,
  actions
}
