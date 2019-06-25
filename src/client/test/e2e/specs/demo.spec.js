/* globals expect describe it $ */
import utils from '../utils'
const uuid = require('uuid/v4')
const name = uuid()

describe("Demo", function () {
  beforeEach(utils.beforeEach)
  afterEach(utils.afterEach)

  it('shows the proper application title', function () {
    return this.app.client.getTitle()
      .then(title => {
        expect(title).to.equal('cte-client')
      })
  })

  it('should create a file', async function () {
    const text = await this.app.client.element('.material-design-icon.file-plus-icon.button').click().keys([name]).element('button.ok').click().element('ul.fileTree').getText()
    return expect(text.split('\n')).to.include(name)
  })

  it('should open a file', async function () {
    const tabFile = 'export default Tab'
    await this.app.client.waitUntilWindowLoaded()
    await this.app.client.element('span=tabType.js').click().waitUntilTextExists('#tabs', 'tabType.js', 3000)
    const text = await this.app.client.element('.editor-pieces').getText()
    const arr = text.split('\n')
    return expect(arr[arr.length - 1]).to.equal(tabFile)
  })
})
