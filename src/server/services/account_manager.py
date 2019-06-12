from service import Service, message_type
from typedefs import Address
import Pyro4
from typing import Dict, List, Tuple


@Pyro4.expose
class AccountManager(Service):
    """
    Service responsible for handling all account related messages.

    Handles: login, logout, account registration, account deletion,
    account management (nomen est omen) and permission-related requests.
    """
    def __init__(self, *super_args):
        super().__init__(*super_args)

        self.usernames: Dict[Address, str] = {}

    @message_type("account-login")
    def login(self, msg):
        pass
