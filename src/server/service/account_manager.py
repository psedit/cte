from service import Service, message_type
from client import Address
import Pyro4
from typing import Dict, List, Tuple


@Pyro4.expose
class AccountManager(Service):
    """
    Service responsible for handling all account related messages.

    Handles: login, logout, account registration, account deletion,
    account management (nomen est omen) and permission-related requests.
    """
    _wanted_msg_types = [
            "account-login"
            ]

    def __init__(self, msg_bus):
        super().__init__(msg_bus)
        self._msg_pass = msg_pass

    @message_type("account-login")
    def login(self, msg):
        pass
