from Client import Address
import Pyro4
from typing import Dict, List, Tuple


@Pyro4.expose
class AccountManager():
    """"""
    def __init__(self, msg_pass):
        self._msg_pass = msg_pass

    def get_wanted_messages():
        pass


    def handle_msg(self, msg):
        pass

    def login(self, addr: Address, uname: str, passwd: str):
        pass



def main():
    # Connect to message handler
    try:
        msg_pass = Pyro4.Proxy("service.message_passer")
    except Exception as e:
        print("Message passer service not reachable")

    # Register Pyro4 daemon
    accman = AccountManager(msg_pass)
    accman_d = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    accman_uri = clist_d.register(accman)
    ns.register("service.accman", accman_uri)

    # Start request loop
    print("AccountManager service running")
    accman_d.requestLoop()


if __name__ == "__main__":
    main()
