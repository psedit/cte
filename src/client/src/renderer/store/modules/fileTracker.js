const state = {
  code: ''
}

const mutations = {
  updateCode (state, newCode) {
    state.code = newCode
    console.log('State is: ' + state.code)
  }
}

const actions = {
  updateCodeAction (state, newCode) {
    state.commit('updateCode', newCode)
  }
}

export default {
  state,
  mutations,
  actions
}
