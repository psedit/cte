from datetime import datetime
from typedefs import Address


class Client():
    """"""
    def __init__(self, addr: Address):
        self.addr = addr
        self.auth = False
        self.uname = ""
        self.conn_time = datetime.now()

    def __str__(self):
        return f"{addr} - {uname}"
