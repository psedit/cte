"""
Lab 3 - Chat Room (Client)
NAME: Sam van Kampen
STUDENT ID: 11874716
DESCRIPTION: A chat room client.
"""

from tkinter import TclError
from gui import MainWindow
from select import select
from socket import socket
import ssl
import traceback

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations('cert.pem')


class Buffer:
    """
    Represents an iterable buffer that returns completed lines.
    """
    def __init__(self):
        """ Initialise the buffer with no contents. """
        self.buffer = ""

    def __iter__(self):
        """ Return the iterator on this object. """
        return self

    def __next__(self):
        """
        Return the next line in the buffer, or raise StopIteration if there
        are no lines left.
        """
        if "\n" not in self.buffer:
            # There is no next line.
            raise StopIteration
        else:
            # There is a line in the buffer.
            # Get the data and assign the rest back to the buffer.
            data, self.buffer = self.buffer.split("\n", 1)
            return data.rstrip()

    def append(self, data):
        """ Append data to the buffer """
        self.buffer += data
        return data


buf = Buffer()


def handle_server_io(w, ssl_sock):
    """
    Reads possible lines from the server, and prints them.
    In case the socket is closed, closes the client.
    """
    while select([ssl_sock], [], [], 1/120)[0] or ssl_sock.pending():
        # Since select works on OS-level sockets, and the SSL layer is above
        # that, there may be data at the SSL layer, but not (yet) at the
        # application layer. Because of this, we use a non-blocking socket and
        # just continue in case there's no data to read.
        try:
            line = ssl_sock.recv(4096).decode('utf-8')
        except ssl.SSLWantReadError:
            continue

        if not line:
            # In this case, the server has closed the connection.
            return w.quit()

        buf.append(line)

    for line in buf:
        w.writeln(line)


def loop(port, cert, ip):
    """
    GUI loop.
    port: port to connect to.
    cert: public certificate (task 3)
    ip: IP to bind to (task 3)
    """
    sock = socket()
    sock.bind((ip, 0))
    sock.connect(('127.0.0.1', port))

    ssl_sock = context.wrap_socket(sock, server_hostname='127.0.0.1')
    ssl_sock.setblocking(False)

    w = MainWindow()
    # update() returns false when the user quits or presses escape.
    while w.update():
        # if the user entered a line getline() returns a string.
        line = w.getline()
        # Handle socket I/O.
        handle_server_io(w, ssl_sock)
        if line:
            ssl_sock.sendall((line+'\n').encode('utf-8'))


# Command line parser.
if __name__ == '__main__':
    import sys
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--port', help='port to connect to',
                   default=12345, type=int)
    p.add_argument('--cert', help='server public cert', default='', type=str)
    p.add_argument('--ip', help='IP to bind to', default='127.0.0.1', type=str)
    args = p.parse_args(sys.argv[1:])
    try:
        loop(args.port, args.cert, args.ip)
    except TclError:
        traceback.print_exc()
        pass
