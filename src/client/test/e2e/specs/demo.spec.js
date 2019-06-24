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
    expect(text.split('\n')).to.include(name)
  })
})
