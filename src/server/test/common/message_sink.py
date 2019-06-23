import Pyro4
import uuid
import time
from typing import List
import queue
import threading


@Pyro4.expose
class MessageSink():
    """
    Sink that accepts a set of messages and can wait for them in a different
    thread.
    """
    def __init__(self, wanted_messages: List[str]):
        self._wanted_messages = wanted_messages
        self.msg_queue: queue.Queue = queue.Queue()
        self._running = True
        self._uuid = str(uuid.uuid4())
        self.name = f"service.MessageSink_{self._uuid}"
        self._start_finished_condition = threading.Condition()
        with self._start_finished_condition:
            self._sink_thread = threading.Thread(target=self.start)
            self._sink_thread.daemon = True
            self._sink_thread.start()
            self._start_finished_condition.wait()


    def get_wanted_messages(self):
        return self._wanted_messages

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

    def disconnect(self):
        self._running = False
        self._ns.remove(self.name)

    def start(self):
        with self._start_finished_condition:
            self._ns = Pyro4.locateNS()
            # Don't need to wait for message bus, because
            # it is waited for by the test setup.

            inst_d = Pyro4.Daemon()
            self._inst_uri = inst_d.register(self)
            self._ns.register(self.name, self._inst_uri)
            self._start_finished_condition.notify()
        inst_d.requestLoop(lambda: self._running)
