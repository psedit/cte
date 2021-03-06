from .typedefs import Address
from .service import Service, message_type
from functools import partial
import traceback
import Pyro4
import asyncio
import json
import websockets
from typing import Dict, List
from collections import defaultdict
import socket
import signal


def handler(*args):
    WSServer._asio_loop.call_soon_threadsafe(WSServer._asio_loop.stop)


signal.signal(signal.SIGUSR1, handler)


def list_ser(obj):
    """
    Try serializing unknown objects as lists.

    This function is here because we use some dataclasses which are not, by
    default, JSON serializable. They can be iterated over, however, and contain
    only JSON serializable objects. Therefore, we simply turn them into lists
    and pass them on to the JSON. This also works well client-side, as the
    dataclasses replaced plain lists.
    """
    return [*obj]


@Pyro4.expose
class WSServer(Service):
    _asio_loop = asyncio.get_event_loop()
    """
    WebSocket server which is also available over Pyro.
    """
    def __init__(self, *super_args):
        super().__init__(*super_args)

        self.clients: Dict[Address, websockets.WebSocketClientProtocol] = {}
        self.messages_to_send: asyncio.Queue = asyncio.Queue()

        self.usernames: Dict[Address, str] = {}
        self.username_counters: Dict[str, int] = defaultdict(int)

    @classmethod
    def start(cls):
        """
        Starts the WebSocket server, hooking Pyro into the asyncio event loop.
        """
        ns = Pyro4.locateNS()
        cls._wait_for_services(ns)

        msg_bus = Pyro4.Proxy("PYRONAME:service.MessageBus")
        logger = Pyro4.Proxy("PYRONAME:meta.Logger")

        inst = cls(msg_bus, logger)
        inst_d = Pyro4.Daemon()
        inst_uri = inst_d.register(inst)

        ns.register("service.WSServer", inst_uri)

        inst.hook_and_start_event_loop(inst_d)

    def hook_and_start_event_loop(self, inst_d: Pyro4.Daemon):
        """
        Hooks Pyro into the asyncio event loop and starts it.
        """
        self._pyro_daemon = inst_d
        self._known_pyro_socks: List[socket.socket] = []
        for sock in inst_d.sockets:
            self._known_pyro_socks.append(sock)
            self._asio_loop.add_reader(
                    sock.fileno(), partial(self.handle_pyro_event, sock)
                )

        self._asio_loop.run_until_complete(
            websockets.serve(self.ws_loop, '0.0.0.0', 12345))
        self._asio_loop.run_forever()

    async def ws_loop(self, websocket, path):
        """
        Handle new messages from a websocket.
        """
        self.clients[websocket.remote_address] = websocket

        read_task = asyncio.create_task(self.ws_read_loop(websocket, path))
        write_task = asyncio.create_task(self.ws_write_loop())

        done, pending = await asyncio.wait([read_task, write_task],
                                           return_when=asyncio.FIRST_COMPLETED)

    def _disconnect_ws(self, client_address):
        username = self.usernames.get(client_address)
        try:
            del self.clients[client_address]
            del self.usernames[client_address]
        except KeyError:
            self._warning(traceback.format_exc())
        self._send_message("client-disconnect",
                           {"address": client_address,
                            "username": username})

    def _maybe_remap_recipients(self, recipients) -> List[Address]:
        if not any(isinstance(i, str) for i in recipients):
            return recipients

        rmap = {v: k for k, v in self.usernames.items()}
        new_rec = [rmap[r] for r in recipients if r in rmap]
        self._info(f"Mapped recipients {recipients} to {new_rec}")
        return new_rec

    async def ws_write_loop(self):
        """
        Write loop for websockets.
        """
        while True:
            msg = await self.messages_to_send.get()
            recipients = msg["content"]["response_addrs"]
            self._info("Sending message %r to clients %r", msg, recipients)
            recipients = self._maybe_remap_recipients(recipients)
            for recipient in recipients:
                try:
                    await self.clients[recipient].send(
                            json.dumps(msg["content"]["msg"], default=list_ser)
                        )
                except Exception:
                    self._warning("Websocket %r unexpectedly disconnected!",
                                  recipient)

                    self._disconnect_ws(recipient)

            self.messages_to_send.task_done()

    async def ws_read_loop(self, websocket, path):
        """
        Read loop for websockets.
        """
        self._info("Connection accepted from %r", websocket.remote_address)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                except json.decoder.JSONDecodeError as e:
                    if 'quote' in e.msg:
                        await websocket.send("Double quotes. Niet single.")
                        continue
                except Exception:
                    continue

                if 'type' not in data or 'content' not in data:
                    print("Unacceptable message (missing type or content)")
                    continue

                new_type = data['type']

                if data['type'] == 'net-send':
                    return  # close the connection.

                uname = self.usernames.get(websocket.remote_address) or "uname"
                client_info = (websocket.remote_address, uname)

                print(f"Received message: {data}")
                self._send_message_from_client(new_type, data['content'],
                                               client_info)
        except Exception:
            print(f'Websocket {websocket} unexpectedly closed connection.')
        finally:
            self._disconnect_ws(websocket.remote_address)

    def handle_pyro_event(self, socket):
        """
        Handle an event on a Pyro fd.
        """
        self._pyro_daemon.events([socket])

        for sock in self._pyro_daemon.sockets:
            if sock not in self._known_pyro_socks:
                self._known_pyro_socks.append(sock)
                self._asio_loop.add_reader(
                        sock.fileno(), partial(self.handle_pyro_event, sock)
                    )

    @message_type("net-send")
    async def send_message(self, msg):
        asyncio.run_coroutine_threadsafe(self.messages_to_send.put(msg),
                                         self._asio_loop)

    @message_type("login-request")
    async def _register_user(self, msg):
        uname = msg["content"]["username"]
        addr = msg["sender"][0]

        if self.usernames.get(addr):
            return self._send_message_client("login-response",
                                             {"succeed": False},
                                             addr)

        username_count = self.username_counters[uname]
        if username_count:
            new_uname = f"{uname}_{username_count}"
        else:
            new_uname = uname

        self.username_counters[uname] += 1
        self.usernames[addr] = new_uname

        self._send_message_client("login-response",
                                  {
                                      "succeed": True,
                                      "new_username": new_uname
                                  },
                                  addr)

    @message_type("client-list-request")
    async def _send_client_list(self, msg):
        clients = list(self.clients.keys())

        content = {
            "client_list": clients
        }

        self._send_message("client-list-response", content,
                           resp_uuid=msg["uuid"])


def main():
    # threading causes weird issues
    Pyro4.config.SERVERTYPE = 'multiplex'
    WSServer.start()


if __name__ == '__main__':
    main()
