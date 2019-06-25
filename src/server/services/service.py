import threading
import inspect
import Pyro4
from typing import Dict, Any, Callable, List, Tuple
import uuid
from typedefs import Address
import time
import asyncio
from collections import defaultdict
from mixins import LoggerMixin


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
class Service(LoggerMixin):
    """
    Super class for services.

    This class implements basic message handling mechanics
    with handle_message and allows for simple message
    sending with send_message.

    This class also implements the Service starting procedure,
    including the outbound connection with the message bus.
    New services can be started using .start (duh).

    Inheriting classes must call super().__init__(message_bus, logger)
    within their own __init__.

    Inheriting classes can declare which message type a certain
    method accepts by adding the @message_type(<type>) decorator,
    where <type> is a string containing the message type name.
    """
    def __init__(self, msg_bus, logger):
        self._msg_bus = msg_bus

        super().__init__(logger)

        self._logname = f"service.{self.__class__.__name__}"

        self._resp_cache: Dict[str, Any] = {}
        self._type_map: Dict[str, Callable[[dict], None]] = {}
        for _, func in inspect.getmembers(
                self, predicate=lambda x: hasattr(x, "_msg_type")):
            self._type_map[func._msg_type] = func

        # TODO: List[Any] -> List[Future] (but need to find type)
        self._waiting: Dict[str, List[Any]] = defaultdict(list)

        self._loop = asyncio.new_event_loop()
        self._handler_lock: asyncio.Lock = asyncio.Lock(loop=self._loop)
        self._msg_queue = asyncio.Queue(loop=self._loop)
        self._async_thread = threading.Thread(target=self._start_async_thread)
        self._async_thread.daemon = True
        self._async_thread.start()

    def _start_async_thread(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._async_read_loop())

    async def _async_read_loop(self):
        async def call_with_lock(msg, fn):
            # Block different handlers from executing concurrently
            # enforcing sequential ordering, since we really only
            # use async for its Future behavior.

            # Is this terrible? Yes. Would I like to have used a
            # different architecture? Maybe. But we have a week
            # left, so this'll do.

            # Also, we're using Python, so it seems fitting to use a
            # far-reaching, concurrency-breaking lock ;)
            async with self._handler_lock:
                await fn(msg)

        while True:
            msg = await self._msg_queue.get()

            handled_future = False

            for future in self._waiting.get(msg.get('response_uuid'), []):
                self._info("Setting result for future.")
                handled_future = True
                future.set_result(msg)

            func = self._type_map.get(msg["type"], False)

            if not func and not handled_future:
                return self._warning(f"Message type {msg['type']} not accepted"
                                     "by service {self.__class__.__name__}")

            if func:
                coro = call_with_lock(msg, func)
                asyncio.create_task(coro)

    async def _wait_for_response(self, uuid: str):
        # should be called from a message handler (i.e. using await)
        fut = asyncio.get_event_loop().create_future()
        self._waiting[uuid].append(fut)
        return await fut

    @staticmethod
    def _wait_for_services(ns):
        while not ('service.MessageBus' in ns.list()
                   and 'meta.Logger' in ns.list()):
            time.sleep(0.05)

    @classmethod
    def start(cls, start_request_loop=True):
        """
        Starting routine for the service.

        Establishes outbound connection to the message bus.
        """
        # Try to establish connection to the message bus
        ns = Pyro4.locateNS()
        cls._wait_for_services(ns)
        msg_bus = Pyro4.Proxy("PYRONAME:service.MessageBus")
        logger = Pyro4.Proxy("PYRONAME:meta.Logger")

        # Register Pyro4 daemon
        inst = cls(msg_bus, logger)
        inst_d = Pyro4.Daemon()
        inst_uri = inst_d.register(inst)
        ns.register(f"service.{cls.__name__}", inst_uri)

        # Start request loop
        print(f"{cls.__name__} service running")
        if start_request_loop:
            inst_d.requestLoop()

    def get_wanted_messages(self):
        """
        Return the list of all message types accepted by this service.
        """
        return [*self._type_map.keys()]

    def handle_message(self, msg):
        """
        Endpoint called by the message bus which calls the appropriate
        service method based on the the received message's type and
        this type's mapping in _type_map.
        """

        msg_str = str(msg)

        if len(msg_str) > 750:
            self._info(f"Received message: {msg_str[:350]}{msg_str[-349:]}")
        else:
            self._info(f"Received message: {msg_str}")
        coro = self._msg_queue.put(msg)
        asyncio.run_coroutine_threadsafe(coro, self._loop)

    def _construct_message(self, msg_type: str, content: Any,
                           pref_dest: str = None,
                           resp_uuid: str = None,
                           client_info: Tuple[Address, str] = None):
        msg_uuid = str(uuid.uuid4())

        sender = f"service.{self.__class__.__name__}"

        msg = {"type": msg_type,
               "uuid": msg_uuid,
               "response_uuid": resp_uuid,
               "sender": client_info if client_info else sender,
               "pref_dest": pref_dest,
               "content": content}
        return msg

    def _send_message(self,
                      msg_type: str,
                      content: Any,
                      pref_dest: str = None,
                      resp_uuid: str = None):
        """
        Assembles all message components and puts the combined message
        on the message bus.
        """
        msg = self._construct_message(msg_type, content, pref_dest, resp_uuid)
        self._msg_bus.put_message(msg)
        return msg

    def _send_message_client(self, msg_type: str, content: Any, *addrs):
        """
        Assembles all message components and puts the combined
        message on the message bus.
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

    def _send_message_from_client(self,
                                  msg_type: str,
                                  content: Any,
                                  client_info):
        msg = self._construct_message(msg_type,
                                      content,
                                      None,
                                      client_info=client_info)
        self._msg_bus.put_message(msg)
        return msg
