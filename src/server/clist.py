import Pyro4


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class ClientList():
    def __init__(self):
        pass


def main():
    clist_d = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    clist_uri = clist_d.register(ClientList)
    ns.register("service.clist", clist_uri)

    clist_d.requestLoop()


if __name__ == "__main__":
    main()
