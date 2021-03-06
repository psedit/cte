import electron from 'electron'
import { Application } from 'spectron'

export default {
  afterEach () {
    this.timeout(10000)

    if (this.app && this.app.isRunning()) {
      return this.app.stop()
    }
  },
  beforeEach () {
    this.timeout(5000)
    this.app = new Application({
      path: electron,
      args: ['dist/electron/main.js'],
      startTimeout: 5000,
      waitTimeout: 5000
    })

    return this.app.start()
  }
}
