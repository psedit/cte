#!/usr/bin/env python3
from functools import partial
import Pyro4
import asyncio
import json
import websockets
from client import Address
from service import Service, message_type

@Pyro4.expose
class WSServer(Service):
    """ WebSocket server which is also available over Pyro. """
    _wanted_msg_types = ["net-send"]

    def __init__(self, msg_bus):
        super().__init__(msg_bus)

        self.clients: Dict[Address, websockets.WebSocketClientProtocol] = []
        self.messages_to_send: asyncio.Queue = asyncio.Queue()

    @classmethod
    def start(cls):
        """ Starts the WebSocket server, hooking Pyro into the asyncio event loop. """
        try:
            msg_bus = Pyro4.Proxy("PYRONAME:service.MessageBus")
        except Exception as e:
            return print("Message bus not available.")

        inst = cls(msg_bus)
        inst_d = Pyro4.Daemon()
        ns = Pyro4.locateNS()
        inst_uri = clist_d.register(inst)

        ns.register("service.WSServer", inst_uri)

        inst.hook_and_start_event_loop(inst_d)

    def hook_and_start_event_loop(self, inst_d: Pyro4.Daemon):
        """ Hooks Pyro into the asyncio event loop and starts it. """
        self._asio_event_loop = asyncio.get_event_loop()
        self._pyro_daemon = inst_d
        self._known_pyro_socks = []
        for sock in inst_d.sockets:
            self._known_pyro_socks.append(sock)
            self._asio_event_loop.add_reader(sock.fileno(),
                    partial(self.handle_pyro_event, sock))

        self._asio_event_loop.run_until_complete(
                websockets.serve(self.ws_loop, 'localhost', 12345))
        self._asio_event_loop.run_forever()

    async def ws_loop(self, websocket, path):
        """ Handle new messages from a websocket. """
        self.clients[(websocket.host, websocket.port)] = websocket

        read_task = asyncio.ensure_future(self.ws_read_loop(websocket, path))
        write_task = asyncio.ensure_future(self.ws_write_loop())

        done, pending = await asyncio.wait([read_task, write_task],
                                           return_when=asyncio.FIRST_COMPLETED)

    async def ws_write_loop(self):
        """ Write loop for websockets. """
        while True:
            msg = await self.messages_to_send.get()
            recipients = msg["content"]["response_addrs"]
            for recipient in recipients:
                await self.clients[recipient].send(msg["content"]["msg"])

    async def ws_read_loop(self, websocket, path):
        """ Read loop for websockets. """
        try:
            async for message in websocket:
                data = json.loads(message)
                new_type = data['type']
                data['request_address'] = (websocket.host, websocket.port)
                self._send_message(new_type, data)
        finally:
            del self.clients[(websocket.host, websocket.port)]

    def handle_pyro_event(self, fd):
        """ Handle an event on a Pyro fd. """
        self._pyro_daemon.events(sock)
        for sock in self._pyro_daemon.sockets:
            if sock not in self._known_pyro_socks:
                self._known_pyro_socks.append(sock)
                self._asio_event_loop.add_reader(sock.fileno(),
                        partial(self.handle_pyro_event, sock))

    @message_type("net-send")
    def send_message(self, msg):
        self.messages_to_send.put_nowait(msg)
        pass


WSServer.start()
