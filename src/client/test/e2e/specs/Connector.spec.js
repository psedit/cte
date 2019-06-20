// import Connector from '../../../src/main/connector'

// describe('Connector', function () {
//   this.timeout(10000)

//   it('should open a connection', (done) => {
//     Connector.addEventListener('open', () => {
//       done()
//     })
//   })

//   it('should listen to a message via addEventListener', function (done) {
//     function wellDone () {
//       done()
//       Connector.removeEventListener('message', wellDone)
//     }

//     Connector.addEventListener('message', wellDone)

//   Connector.send(
//     'file-content-request',
//     {
//       start: 0,
//       length: -1,
//       file: 'file.txt'
//     })
// })

// it('should not listen to a message after removeEventListener', function (done) {
//   function dontCallMe () {
//     done(false)
//   }
//   Connector.addEventListener('message', dontCallMe)
//   Connector.removeEventListener('message', dontCallMe)
//   Connector.send(
//     'file-content-request',
//     {
//       start: 1,
//       length: -1,
//       file: 'file.txt'
//     })

//   setTimeout(done, 1000)
// })

// it('should listen to a specific message via listenToMsg', function (done) {
//   function wellDone () {
//     done()
//     Connector.removeEventListener('message', wellDone)
//   }

//   Connector.listenToMsg('file-content-response', wellDone)

//   Connector.send(
//     'file-content-request',
//     {
//       start: 2,
//       length: -1,
//       file: 'file.txt'
//     })
// })

// it('should get a response of a request', function (done) {
//   Connector.request(
//     'file-content-request',
//     'file-content-response',
//     {
//       start: 3,
//       length: -1,
//       file: 'file.txt'
//     }).then(() => done())
// })
// })
