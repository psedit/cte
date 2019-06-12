import Pyro4
import time
from collections import defaultdict
from typing import Callable, Dict, List
import queue
import threading
from typedefs import UUID, ServiceAddress

from handler_code import HandlerCode


@Pyro4.expose
class MessageBus:
    """
    Passes messages between different services.

    Lets services register themselves for message types by monitoring
    the Pyro name server, and calling .get_wanted_messages when a new
    service is detected.

    Services can put messages on the bus using .put_message.
    """
    def __init__(self) -> None:
        # The message queue
        self.mqueue: queue.Queue = queue.Queue()

        self.response_map: Dict[UUID, ServiceAddress] = {}

        # type -> URI handler map.
        # Can be edited by multiple threads, so there's a lock here.
        self._handler_lock = threading.Lock()
        self.handlers: Dict[str, List[str]] = defaultdict(list)

        # name -> pyro proxy map
        self._proxy_lock = threading.Lock()
        self._proxies: Dict[str, Pyro4.Proxy] = {}

        # A thread which sends the messages from the queue
        self._handler_thread = threading.Thread(target=self._handle_messages)
        self._handler_thread.daemon = True
        self._handler_thread.start()

        # Name server service detection stuff
        self._ns = Pyro4.locateNS()
        self._known_services: Dict[str, str] = {}

        # A thread which polls the nameserver
        # every second for new services.
        self._poll_ns_thread = threading.Thread(target=self._poll_ns)
        self._poll_ns_thread.daemon = True
        self._poll_ns_thread.start()

    def _get_proxy(self, to_uri: str, name: str = None):
        """
        Get a proxy for a given Pyro URI. Adds it to the _proxy
        dictionary, so it can be retrieved quickly later.
        """
        name = name or to_uri
        with self._proxy_lock:
            if name in self._proxies:
                return self._proxies[name]
            else:
                self._proxies[name] = Pyro4.Proxy(to_uri)
                return self._proxies[name]

    def put_message(self, msg: dict):
        """ Put a message on the message queue. """
        if 'type' not in msg:
            return False

        if isinstance(msg['sender'], str) and msg['type'].endswith('request'):
            print(f"Request sent with uuid: {msg['uuid']}")
            self.response_map[msg['uuid']] = msg['sender']

        self.mqueue.put(msg)
        return True

    def _poll_ns(self):
        """
        Poll the name server for new services.
        When those are detected, calls _handle_new_services.
        """
        print(f"Started NS polling thread.")
        while True:
            time.sleep(1)
            new_services: Dict[str, str] = {}
            current_services = self._ns.list()

            for name, uri in current_services.items():
                if name not in self._known_services:
                    new_services[name] = uri

            if new_services:
                print(f"Found new services {new_services}")
                self._handle_new_services(new_services)
            self._known_services = current_services

    def _handle_new_services(self, new_services: Dict[str, str]):
        """ Registers new services. """
        for name, uri in new_services.items():
            if (name == 'service.MessageBus'):
                continue
            if (not name.startswith('service')):
                continue
            proxy = self._get_proxy(uri, name)
            self._register_service_handlers(proxy, uri)

    def _register_service_handlers(self, proxy, uri: str):
        """ Registers which messages a new service wants to receive. """
        with self._handler_lock:
            for mtype in proxy.get_wanted_messages():
                self.handlers[mtype].append(uri)

    def _try_handle_response(self, message):
        if not message['type'].endswith('response'):
            return False

        response_uuid = message.get('response_uuid')

        request_sender = self.response_map.get(response_uuid)
        if not request_sender:
            return False

        self._proxies[request_sender].handle_message(message)
        del self.response_map[response_uuid]
        return True

    def _handle_messages(self):
        """ Waits for new messages in the message queue. """
        while True:
            message = self.mqueue.get()
            handled = self._try_handle_response(message)

            with self._handler_lock:
                handlers = self.handlers[message["type"]]
                if handlers:
                    print(f"Calling handlers for message {message}")
                for uri in handlers:
                    print(f"Calling handle_message on URI {uri}")
                    handled = True
                    retcode = self._get_proxy(uri).handle_message(message)
                    if (retcode == HandlerCode.Halt):
                        break
            if not handled:
                # Puts a message back on the queue if it was not handled.
                # This may cause some problematic behaviour, but it has
                # upsides, too (like messages being sent before services
                # come online).
                self.mqueue.put(message)


mb = MessageBus()

if __name__ == '__main__':
    Pyro4.Daemon.serveSimple({
        mb: 'service.MessageBus'
    }, ns=True)
