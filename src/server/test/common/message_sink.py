import Pyro4
import queue
import threading

class MessageSink():
    """ Sink that accepts all messages. """
    def __init__(self):
        self.msg_queue = queue.Queue()
        self._sink_thread = threading.Thread(target=self.start)
        self._sink_thread.daemon = True
        self._sink_thread.start()

    def get_wanted_messages(self):
        return ['all']

    def handle_message(self, msg):
        self.msg_queue.put(msg)

    def wait_for(self, message_type, timeout=2):
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            try:
                msg = self.msg_queue.get(timeout=timeout)
                if msg['type'] == message_type:
                    return msg
            except queue.Empty:
                return False

    def start(self):
        ns = Pyro4.locateNS()
        # Don't need to wait for message bus, because
        # it is waited for by the test setup.

        msg_bus = Pyro4.Proxy("PYRONAME:service.MessageBus")

        inst_d = Pyro4.Daemon()
        inst_uri = inst_d.register(self)
        ns.register(f"service.MessageSink", inst_uri)

        inst_d.requestLoop()