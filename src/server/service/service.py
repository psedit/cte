import inspect
import Pyro4
from typing import Dict, Any
import uuid


class Service():
    """"""
    def __init__(self, msg_pass):
        self._msg_pass = msg_pass

    def message_type(msg_t: str):
        def decorator(f):
            f._type = msg_t
            return f
        return decorator

    @classmethod
    def start(cls):
        """"""
        try:
            msg_pass = Pyro4.Proxy("service.MessagePasser")
        except Exception as e:
            print("Message passer service not reachable")

        # Register Pyro4 daemon
        inst = cls(msg_pass)
        inst_d = Pyro4.Daemon()
        ns = Pyro4.locateNS()
        inst_uri = clist_d.register(accman)
        ns.register(f"service.{cls.__name__}", inst_uri)

        # Start request loop
        print(f"{cls.__name__} service running")
        inst_d.requestLoop()

    def handle_message(self, msg):
        for func_name, func in inspect.getmembers(self, predicate=lambda x: x._type==msg["type"]):
            f(msg)

    def send_message(self, msg_t: str, content: Dict[Any, Any], pref_dest: str=None):
        msg_uuid = uuid.uuid()
        msg = {"type": msg_type,
               "uuid": msg_uuid,
               "sender": self.__name__,
               "pref_dest": pref_dest,
               "content": content}
        self._msg_pass.put_message(msg)
        return msg



