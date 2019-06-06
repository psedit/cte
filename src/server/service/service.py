import inspect
import Pyro4
from typing import Dict, Any, Callable, List
import uuid


def message_type(msg_type: str):
    """
    Decorator used with Service functions to signal
    which message type it handles.
    """
    def decorator(f):
        f._msg_type = msg_type
        return f
    return decorator


@Pyro4.expose
class Service():
    """
    Super class for services.

    This class implements basic message handling mechanics
    with handle_message and allows for simple message
    sending with send_message.

    This class also implements the Service starting procedure,
    including the outbound connection with the message bus.
    New services can be started using .start (duh).

    Inheriting classes must call super().__init__(message_bus)
    within their own __init__. This init must take the message
    bus as its only argument (except for self, of course).

    Inheriting classes can reassign the _wanted_msg_types variable
    to include the various message types the service accepts.

    Inheriting classes can declare which message type a certain
    method accepts by adding the @message_type(<type>) decorator,
    where <type> is a string containing the message type name.
    """
    _wanted_msg_types: List[str] = []

    def __init__(self, msg_bus):
        self._msg_bus = msg_bus
        self._resp_cache: Dict[str, Any] = {}
        self._type_map: Dict[str, Callable[[dict], None]] = {}
        for _, func in inspect.getmembers(self, predicate=lambda x: hasattr(x, "_msg_type")):
            self._type_map[func._msg_type] = func

    @classmethod
    def start(cls):
        """
        Starting routine for the service.

        Establishes outbound connection to the message bus.
        """
        # Try to establish connection to the message bus
        try:
            msg_bus = Pyro4.Proxy("PYRONAME:service.MessageBus")
        except Exception as e:
            print("Message passer service not reachable")

        # Register Pyro4 daemon
        inst = cls(msg_bus)
        inst_d = Pyro4.Daemon()
        ns = Pyro4.locateNS()
        inst_uri = clist_d.register(accman)
        ns.register(f"service.{cls.__class__.__name__}", inst_uri)

        # Start request loop
        print(f"{cls.__name__} service running")
        inst_d.requestLoop()

    def get_wanted_messages(self):
        """
        Return the list of all message types accepted by this service.
        """
        return self._wanted_msg_types

    def handle_message(self, msg):
        """
        Endpoint called by the message bus which calls the appropriate
        service method based on the the received message's type and
        this type's mapping in _type_map.
        """
        try:
            self._type_map[msg["type"]](msg)
        except KeyError:
            print(f"Message type {msg['type']} not accepted by service {self.__class__.__name__}")

    def _construct_message(self, msg_type: str, content: Any, pref_dest: str = None):
        msg_uuid = uuid.uuid4()
        msg = {"type": msg_type,
               "uuid": msg_uuid,
               "sender": self.__class__.__name__,
               "pref_dest": pref_dest,
               "content": content}
        return msg

    def _send_message(self, msg_type: str, content: Any, pref_dest: str = None):
        """
        Assembles all message components and puts the combined message on the message bus.
        """
        msg = self._construct_message(msg_type, content, pref_dest)
        self._msg_bus.put_message(msg)
        return msg

    def _send_message_client(self,  msg_type: str, content: Any, *addrs):
        """
        Assembles all message components and puts the combined message on the message bus.
        Only for messages destined for a client.
        """
        client_msg = self._construct_message(msg_type, content)
        net_cont = {
                "response_addrs": addrs,
                "msg": client_msg
                }
        net_msg = self._construct_message("net-send", net_cont)
        self._msg_bus.put_message(net_msg)
        return net_msg

