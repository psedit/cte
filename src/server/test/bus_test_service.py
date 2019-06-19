import traceback
import Pyro4


@Pyro4.expose
class Test:
    def __init__(self, bus):
        self.bus = bus

    def get_wanted_messages(self):
        return {'busTest'}

    def handle_message(self, message: dict):
        print(f"Got message {message}")


if __name__ == '__main__':
    # Connect to message handler
    try:
        msg_bus = Pyro4.Proxy("PYRONAME:service.MessageBus")
    except Exception:
        traceback.print_exc()
        print("Message passer service not reachable")

    # Register Pyro4 daemon
    test = Test(msg_bus)
    test_d = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    test_uri = test_d.register(test)
    ns.register("service.test", test_uri)

    # Start request loop
    print("Test service running")
    test_d.requestLoop()
