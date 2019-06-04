"""

cte client interface - parsing/queuing code

"""

import sys
import argparse
import socket
import logging
import traceback
import inspect
import re
import ssl
from functools import wraps
from datetime import datetime
from select import select
from typing import List, Dict, Union, ValuesView, Tuple, Any
import ipaddress

LOGFMT = "[%(asctime)s] [%(levelname)7s] %(name)7s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=LOGFMT)
logger = logging.getLogger("server")

NICK_RE = re.compile("^[A-Za-z0-9]+$")

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('./cert.pem', './key.pem')

class Client:
    """ A client of our chat server. """
    def __init__(self, sock, addr: Tuple[str, int]) -> None:
        self.sock = sock
        self.sfile = sock.makefile()
        self.addr = addr

    def __getattr__(self, name: str):
        """ If we don't have self.<name>, try to find self.sock.<name>. """
        return getattr(self.sock, name)

    def send(self, line: str):
        """ Send a message to this client. """
        self.sock.sendall((line + '\n').encode('utf-8'))

    def readline(self) -> str:
        """ Read a line of data from this client. """
        line: str
        try:
            line = self.sfile.readline()
        except (ConnectionResetError, BrokenPipeError):
            line = ''
        return line

    def __repr__(self) -> str:
        """ String representation of this client. """
        addr_str = ':'.join(map(str, self.addr))
        return f"<Client: ({addr_str})>"


class Server:
    """
    The server which interfaces with the clients.

    Binds to the given port with an SSL socket, and listens for incoming
    connections. After connecting, clients can send messages, which the server
    passes to the event handling system.
    """
    def __init__(self, port: int) -> None:
        self.port = port
        self.sock = socket.socket()
        self.keep_listening = True

        self.clients:  List[Client] = []

    def send_clients(self, clients: List[Client], *send_args):
        """ Send <args> to the given list of clients. """
        clients = clients or self.clients
        for client in clients:
            client.send(*send_args)

    def send_others(self, exclude: Client, *send_args):
        """ Send <args> to every client but <exclude>. """
        self.send_clients([c for c in self.clients if c != exclude],
                          *send_args)

    def send_all(self, *send_args: Any):
        """ Send <args> to all clients. """
        self.send_clients(self.clients, *send_args)

    def serve(self):
        """
        Register handlers, bind the socket and listen for clients.
        When a client connects, add them to the client list.
        When there is a message from a client, process it.
        """
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.sock.bind(('127.0.0.1', self.port))
        self.sock.listen(5)

        with context.wrap_socket(self.sock, server_side=True) as ssock:
            while self.keep_listening:
                read, write, error = select([ssock, *self.clients], [], [])

                if ssock in read:
                    self.accept_new_client(ssock)
                    read.remove(ssock)
                for client in read:
                    self.read_and_process(client)

    def disconnect_client(self, client: Client):
        """ Disconnect a given client and remove them from the client list. """
        client.sock.shutdown(socket.SHUT_RDWR)
        client.sock.close()
        try:
            self.clients.remove(client)
        except ValueError:
            pass

    def accept_new_client(self, ssock: ssl.SSLSocket):
        """
        Accept a new client from ssock.
        """
        try:
            sock, addr = ssock.accept()
        except OSError:
            return

        sock.setblocking(False)
        client = Client(sock, addr)
        logger.debug(f"Accepted client {client}")

        self.clients.append(client)

    def read_and_process(self, client: Client):
        """
        Tries to read a line from the client. If the read fails, returns.
        If the read is empty, the client has disconnected; the client is
        thus removed from the client list.

        If a line is read successfully, passes it to .process_line.
        """
        try:
            line = client.readline()
        except ssl.SSLWantReadError:
            return

        if not line:
            logger.debug(f"{client} disconnected.")
            self.disconnect_client(client)

        try:
            self.process_line(client, line.strip())
        except BaseException:
            traceback.print_exc()

    def process_line(self, client: Client, line: str):
        """ Process a line from the client. """
        logger.debug(f"Message from {client}: {line}")


def serve(port):
    """
    Server entry point.
    port: The port to listen on.
    """
    server = Server(port)
    server.serve()


# Command line parser.
if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--port', help='port to listen on', default=12345, type=int)
    args = p.parse_args(sys.argv[1:])
    serve(args.port)
