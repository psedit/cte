from datetime import datetime
from typing import Tuple


# Type definition for client address
Address = Tuple[str, int]


class Client():
    """"""
    def __init__(self, addr: Address):
        self.addr = addr
        self.auth = False
        self.uname = ""
        self.conn_time = datetime.now()

    def __str__(self):
        return f"{addr} - {uname}"
