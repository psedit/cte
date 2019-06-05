from Client import Address
import Pyro4
from typing import Dict, List, Tuple


@Pyro4.expose
class AccountManager():
    """"""
    def __init__(self, msg_pass):
        self._msg_pass = msg_pass

    def login(self, addr: Address, uname: str, passwd: str):
        pass


