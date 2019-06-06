from client import Client, Address
import Pyro4
from typing import Dict, List, Tuple


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class ClientList():
    """
    Service responsible for keeping track of all connected clients
    and handling client related inquiries.
    """
    def __init__(self, msg_pass) -> None:
        self._msg_pass = msg_pass
        self._clients: Dict[Address, Client] = {}

    def handle_msg(self, msg):
        pass

    def get_list(self) -> Dict[Address, Client]:
        return self._clients

    def add_client(self, addr: Address) -> None:
        client: Client = Client(addr)
        self._clients[addr] = client

    def rem_client(self, addr: Address) -> None:
        del self._clients[addr]

    def auth_client(self, addr: Address, uname: str) -> None:
        self._clients[addr].auth = True
        self._clients[addr].uname = uname

    def unauth_client(self, addr: Address) -> None:
        self._clients[addr].auth = False
        self._clients[addr].uname = ""


def main():
    # Connect to message handler
    try:
        msg_pass = Pyro4.Proxy("service.message_passer")
    except Exception as e:
        print("Message passer service not reachable")

    # Register Pyro4 daemon
    clist = ClientList(msg_pass)
    clist_d = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    clist_uri = clist_d.register(clist)
    ns.register("service.clist", clist_uri)

    # Start request loop
    print("ClientList service running")
    clist_d.requestLoop()


if __name__ == "__main__":
    main()
