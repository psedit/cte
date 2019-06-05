from clist_t import Client, Address
import Pyro4
from typing import Dict, List, Tuple


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class ClientList():
    def __init__(self) -> None:
        self.clients: Dict[Address, Client] = {}

    def get_list(self) -> Dict[Address, Client]:
        return self.clients

    def add_client(self, addr: Address) -> None:
        client: Client = Client(addr)
        self.clients[addr] = client

    def rem_client(self, addr: Address):
        del self.clients[addr]

    def auth_client(self, addr: Address, uname: str):
        self.clients[addr].auth = True
        self.clients[addr].uname = uname


def main():
    clist_d = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    clist_uri = clist_d.register(ClientList)
    ns.register("service.clist", clist_uri)

    clist_d.requestLoop()


if __name__ == "__main__":
    main()
