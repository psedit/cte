/* globals expect describe it */
import utils from '../utils'
const uuid = require('uuid/v4')
const name = uuid()

describe('Demo', function () {
  beforeEach(utils.beforeEach)
  afterEach(utils.afterEach)

  it('shows the proper application title', function () {
    return this.app.client.getTitle()
      .then(title => {
        expect(title).to.equal('cte-client')
      })
  })

  it('should create a file', function () {
    return this.app.client.element('.material-design-icon.file-plus-icon.button').click().keys([name]).element('button.ok').click().element('ul.fileTree').getText().waitUntilTextExists(`span=${name}`, name, 3000)
  })

  it('should open a file', async function () {
    const tabFile = 'export default Tab'
    await this.app.client.waitUntilWindowLoaded()
    await this.app.client.waitUntilTextExists('span=tabType.js', 'tabType.js', 10000)
    await this.app.client.element('span=tabType.js').click().waitForVisible('.CodeMirror-lines', 10000)
    const text = await this.app.client.element('.editor-pieces').getText()
    const arr = text.split('\n')
    return expect(arr[arr.length - 1]).to.equal(tabFile)
  })
})