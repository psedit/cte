from client import Address
import Pyro4
from typing import Dict, List, Tuple


@Pyro4.expose
class AccountManager():
    """
    Service responsible for handling all account related messages.

    Handles: login, logout, account registration, account deletion,
    account management (nomen est omen) and permission-related requests.
    """
    def __init__(self, msg_pass):
        self._msg_pass = msg_pass

    def login(self, addr: Address, uname: str, passwd: str):
        pass


