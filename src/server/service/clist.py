import Pyro4
import time


class Client():
    def __init__(self, addr):
        self.addr = addr
        self.auth = False
        self.uname = ""
        self.conn_time = time.time()

    def __str__(self):
        return f"{addr} - {uname}"


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class ClientList():
    def __init__(self):
        self.clients = {}

    def get_list(self):
        return self.clients

    def add_client(self, addr):
        client: Client = Client(addr)
        self.clients[addr] = client

    def rem_client(self, addr):
        del self.clients[addr]

    def auth_client(self, addr, uname):
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
