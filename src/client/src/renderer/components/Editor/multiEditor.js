import CodeMirror from 'codemirror/lib/codemirror'

CodeMirror.defineMode('multi_editor', function (config, parserConfig) {
  const lang = parserConfig.lang
  const mode = CodeMirror.modes.hasOwnProperty(lang) ? CodeMirror.modes[lang] : CodeMirror.modes.null
  const modeInstance = mode(config, parserConfig)
  const startState = parserConfig.startState

  if (startState) {
    modeInstance.startState = () => startState
  }

  return modeInstance
})
