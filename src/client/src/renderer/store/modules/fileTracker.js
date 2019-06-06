const state = {
  code: ''
}

const mutations = {
  updateCode (state, newCode) {
    console.log(newCode)
    state.code = newCode
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
