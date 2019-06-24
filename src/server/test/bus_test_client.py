import Pyro4

mb = Pyro4.Proxy('PYRONAME:service.MessageBus')
mb.put_message({'type': 'busTest', 'value': 42})
