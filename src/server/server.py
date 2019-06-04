"""
Lab 3 - Chat Room (Server)
NAME: Sam van Kampen
STUDENT ID: 11874716
DESCRIPTION: A chat server
"""

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
logger = logging.getLogger("chatd")

NICK_RE = re.compile("^[A-Za-z0-9]+$")

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('./cert.pem', './key.pem')


def name_iter():
    """ Generates 'random' names. """
    names = "Jesse Steijn Mark Leon Justin".split()
    n = 0
    while True:
        suffix, idx = divmod(n, len(names))
        yield names[idx] + str(suffix or '')
        n += 1


names = name_iter()


class Client:
    """ A client of our chat server. """
    def __init__(self, sock, addr: Tuple[str, int]) -> None:
        self.sock = sock
        self.sfile = sock.makefile()
        self.addr = addr
        self.nick = next(names)
        self.admin = False
        self.logged_in = False

    def __getattr__(self, name: str):
        """ If we don't have self.<name>, try to find self.sock.<name>. """
        return getattr(self.sock, name)

    def send(self, line: str):
        """ Send a message to this client. """
        date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        line = f"[{date}] {line}\n"
        self.sock.sendall(line.encode('utf-8'))

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
        admin_str = ' (admin)' if self.admin else ''
        addr_str = ':'.join(map(str, self.addr))
        return f"<Client: {self.nick} ({addr_str}){admin_str}>"


def handles(cmd):
    """ Marks a function as handling a given command. """
    def decorator(fn):
        fn._handles = cmd
        return fn
    return decorator


def admin_only(fn):
    """ Marks a command as being admin-only. """
    @wraps(fn)
    def new_fn(self, client: Client, args: str):
        if not client.admin:
            return client.send("You need to be an admin to use this command")
        return fn(self, client, args)
    return new_fn


class UserData:
    """ Data about a user, such as their password and admin status. """
    def __init__(self, password, admin):
        self.password = password
        self.admin = admin


class ChatServer:
    """
    A chat server.

    Binds to the given port with an SSL socket, and listens for incoming
    connections. After connecting, clients can send messages, which are
    potentially relayed to other clients.
    """
    def __init__(self, port: int) -> None:
        self.port = port
        self.sock = socket.socket()
        self.keep_listening = True

        self.clients:  Dict[str, Client] = {}
        self.messages: List[Tuple[str, str, str]] = []
        self.bans:     List[str] = []
        self.userdata: Dict[str, UserData] = {}

    def send_clients(self, clients: Union[List[Client], ValuesView[Client]],
                     *send_args):
        """ Send <args> to the given list of clients. """
        clients = clients or self.clients.values()
        for client in clients:
            client.send(*send_args)

    def send_others(self, exclude: Client, *send_args):
        """ Send <args> to every client but <exclude>. """
        self.send_clients([c for c in self.clients.values() if c != exclude],
                          *send_args)

    def send_all(self, *send_args: Any):
        """ Send <args> to all clients. """
        self.send_clients(self.clients.values(), *send_args)

    def setup_handlers(self):
        """ Loads handlers from the current instance. """
        members = [*dict(inspect.getmembers(self)).values()]
        handlers = {}

        for member in members:
            if hasattr(member, '_handles'):
                handlers[member._handles] = member

        self.handlers = handlers

    def serve(self):
        """
        Register handlers, bind the socket and listen for clients.
        When a client connects, add them to the client list.
        When there is a message from a client, process it.
        """
        self.setup_handlers()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.sock.bind(('127.0.0.1', self.port))
        self.sock.listen(5)

        with context.wrap_socket(self.sock, server_side=True) as ssock:
            while self.keep_listening:
                read, write, error = select([ssock, *self.clients.values()],
                                            [], [])

                if ssock in read:
                    self.accept_new_client(ssock)
                    read.remove(ssock)
                for client in read:
                    self.read_and_process(client)

        return client.addr[0] in self.bans

    def disconnect_client(self, client: Client):
        """ Disconnect a given client and remove them from the client list. """
        client.sock.shutdown(socket.SHUT_RDWR)
        client.sock.close()
        try:
            del self.clients[client.nick]
        except KeyError:
            pass

    def accept_new_client(self, ssock: ssl.SSLSocket):
        """
        Accept a new client from ssock.

        If the client is banned, disconnect immediately.
        Additionally, send a connection notification to the currently
        connected clients.
        """
        try:
            sock, addr = ssock.accept()
        except OSError:
            return

        sock.setblocking(False)
        client = Client(sock, addr)
        logger.debug(f"Accepted client {client}")

        if client.addr[0] in self.bans:
            client.send("You're banned.")
            self.disconnect_client(client)
            return

        self.send_others(client, f"Connect: {client.nick}.")
        self.clients[client.nick] = client

        client.send("Connected to server.")
        # Send the current client list to the client, too.
        self.list(client, None)

    def read_and_process(self, client: Client):
        """
        Tries to read a line from the client. If the read fails, returns.
        If the read is empty, the client has disconnected; sends a disconnect
        notification to the other clients and removes the client from the
        client list.

        If a line is read successfully, passes it to .process_line.
        """
        try:
            line = client.readline()
        except ssl.SSLWantReadError:
            return

        if not line:
            logger.debug(f"{client} disconnected.")
            client.sock.close()
            del self.clients[client.nick]
            self.send_others(client, f"Disconnect: {client.nick}")
            return

        try:
            self.process_line(client, line.strip())
        except BaseException:
            traceback.print_exc()

    def process_line(self, client: Client, line: str):
        """ Process a line from the client. """
        args: str = ''
        if line.startswith('/'):
            cmd, *rest = line.split(' ', 1)
            cmd = cmd[1:]
            if rest:
                args = rest[0]
        else:
            cmd = 'say'
            args = line

        handler = self.handlers.get(cmd)

        if handler:
            handler(client, args)
        else:
            logger.warning(f"Unrecognised command {cmd}")

        logger.debug(f"Message from {client}: {line}")

    def date(self) -> str:
        """ Return the current date and time. """
        return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    @handles('say')
    def say(self, client: Client, args: str):
        """ /say <text> - say something. """
        self.messages.append((self.date(), client.nick, args))
        self.send_all(f"<{client.nick}> {args}")

    @handles('whisper')
    def whisper(self, client: Client, args: str):
        """ /whisper <nick> <text> - send a private message to someone. """
        try:
            to_user, text = args.split(' ', 1)
        except ValueError:
            return client.send(f"Usage: {self.whisper.__doc__}")

        target = self.clients.get(to_user)
        if not target:
            return client.send(f"{to_user} does not exist.")

        client.send(f"Whispered {text} to {target.nick}")
        target.send(f"{client.nick} whispers: {text}")

    @handles('list')
    def list(self, client: Client, args: str):
        """ /list - list all currently connected clients. """
        names = ', '.join(self.clients.keys())
        client.send(f"Current users: {names}")

    @handles('whois')
    def whois(self, client: Client, args: str):
        """ /whois <nick> - find out information about someone. """
        if not args:
            return client.send(f"Usage: {self.whois.__doc__}")

        if args not in self.clients:
            return client.send(f"{args} is not a (connected) user.")

        client.send(f"{args} is {self.clients[args]}.")

    @handles('nick')
    def nick(self, client: Client, args: str):
        """ /nick <new_nick> - changes your nickname. """
        if not args:
            return client.send(f"Usage: {self.nick.__doc__}")

        if not NICK_RE.match(args):
            return client.send(f"Invalid nick '{args}', must be [A-Za-z0-9]+.")

        if args in self.clients:
            return client.send("Nick already taken.")

        if args in self.userdata:
            return client.send("Use login instead; this nick is registered.")

        if args in self.bans:
            return client.send("That nickname is banned.")

        # Switch the registered nick over if the client is registered.
        if client.nick in self.userdata:
            user = self.userdata[client.nick]
            del self.userdata[client.nick]
            self.userdata[args] = user

        self.internal_nick(client, args)

    def internal_nick(self, client, new_nick):
        """ Switch map keys around and send notification for nickchange. """
        if client.nick == new_nick:
            return

        del self.clients[client.nick]
        old_nick = client.nick
        client.nick = new_nick
        self.clients[client.nick] = client
        self.send_all(f"** Nickchange: {old_nick} -> {new_nick}")

    @handles('?')
    def help_q(self, *args):
        """ /? - see /help """
        self.help(*args)

    @handles('help')
    def help(self, client: Client, args: str):
        """ /help - you're looking at it. """
        # Since all of the commands have docstrings, just send those.
        client.send("** Help:")
        for cmd, fn in self.handlers.items():
            client.send(fn.__doc__)

    @handles('me')
    def me(self, client: Client, args: str):
        """ /me <action> - perform an action. """
        self.send_all(f"* {client.nick} {args}")

    @handles('search')
    def search(self, client: Client, args: str):
        """ /search <n> <text> - Print at most n messages that match text. """
        try:
            max_str, text = args.split(' ', 1)
            maximum = int(max_str)
        except ValueError:
            return client.send(f"Invalid maximum or not enough arguments.")

        matches = [(date, user, msg) for date, user, msg in self.messages
                   if text in msg]

        client.send(f"** Matches for '{text}':")
        for date, user, match in matches[-maximum:]:
            client.send(f"** [{date}] <{user}> {match}")
        client.send("** End of matches.")

    @handles('register')
    def register(self, client: Client, args: str):
        """ /register <password> - Register with the given password. """
        if not args:
            return client.send(f"Usage: {self.register.__doc__}")

        if ' ' in args:
            return client.send("Invalid password (can't contain spaces)")

        password = args
        self.userdata[client.nick] = UserData(password, False)
        client.send("You are now registered.")

    @handles('admin')
    def admin(self, client: Client, args: str):
        """ /admin <password> - mark yourself as an admin. """
        if not args:
            return client.send(f"Usage: {self.admin.__doc__}")

        if client.nick not in self.userdata:
            return client.send("You need to register first!")

        if not client.logged_in:
            return client.send("You need to login first!")

        if args == 'password':
            client.admin = True
            self.userdata[client.nick].admin = True
            client.send("You're now an admin.")
        else:
            client.send("That's the wrong password.")

    @handles('login')
    def login(self, client: Client, args: str):
        """ /login <nick> <password> """
        try:
            nick, password = args.split()
        except ValueError:
            return client.send(f"Not enough args.")

        if nick in self.bans:
            client.send("You're banned, bye.")
            return self.disconnect_client(client)

        if nick in self.userdata and self.userdata[nick].password == password:
            client.admin = self.userdata[nick].admin
            self.internal_nick(client, nick)
            client.logged_in = True
            return client.send(f"You're logged in as {nick}.")

        client.send("Invalid password or not registered.")

    @handles('ban')
    @admin_only
    def ban(self, client: Client, args: str):
        """ /ban <user> - Ban a registered user. """
        if not args:
            client.send(f"Usage: {self.ban.__doc__}")

        if args not in self.userdata:
            return client.send("Can't ban a client which has no associated " +
                               "user. Just use /kick.")

        self.bans.append(args)
        self.kick(client, args)

    @handles('kick')
    @admin_only
    def kick(self, client: Client, args: str):
        """ /kick <user> - Kick a user. """
        if not args:
            client.send(f"Usage: {self.kick.__doc__}")

        if args not in self.clients:
            return client.send("Not kicking unconnected client.")

        self.clients[args].send("You've been kicked.")
        self.disconnect_client(self.clients[args])

    @handles('banip')
    @admin_only
    def banip(self, client: Client, args: str):
        """ /banip <ip> - ban an IP address. """
        if args not in self.clients:
            return client.send("Invalid user.")

        args = self.clients[args].addr[0]
        self.bans.append(args)
        for cl2 in self.clients.copy().values():
            if args == cl2.addr[0]:
                self.kick(client, cl2.nick)


def serve(port):
    """
    Chat server entry point.
    port: The port to listen on.
    """
    server = ChatServer(port)
    server.serve()


# Command line parser.
if __name__ == '__main__':
    import sys
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--port', help='port to listen on', default=12345, type=int)
    args = p.parse_args(sys.argv[1:])
    serve(args.port)
