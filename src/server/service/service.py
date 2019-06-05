import inspect
import Pyro4
from typing import Dict, Any
import uuid


def message_type(msg_t: str):
    def decorator(f):
        f._type = msg_t
        return f
    return decorator


class Service():
    """"""
    self._wanted_msg_types = []

    def __init__(self, msg_bus):
        self._msg_bus = msg_bus
        self._resp_cache: Dict[str, Any]

    @classmethod
    def start(cls):
        """"""
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
        print(f"{cls.__class__.__name__} service running")
        inst_d.requestLoop()

    def get_wanted_messages(self):
        return self._wanted_msg_types

    def handle_message(self, msg):
        for func_name, func in inspect.getmembers(self, predicate=lambda x: x._type==msg["type"]):
            f(msg)

    def send_message(self, msg_t: str, content: Any, pref_dest: str=None):
        msg_uuid = uuid.uuid()
        msg = {"type": msg_type,
               "uuid": msg_uuid,
               "sender": self.__name__,
               "pref_dest": pref_dest,
               "content": content}
        self._msg_bus.put_message(msg)
        return msg
