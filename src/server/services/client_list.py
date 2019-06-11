# from service import Service, message_type
# from client import Client, Address
# import Pyro4
# from typing import Dict, List, Tuple


# @Pyro4.expose
# @Pyro4.behavior(instance_mode="single")
# class ClientList(Service):
#     """
#     Service responsible for keeping track of all connected clients
#     and handling client related inquiries.
#     """
#     _wanted_msg_types = [
#             "client-list-request",
#             "client-add",
#             "client-remove",
#             "client-authorize",
#             "client-unauthorize"
#             ]

#     def __init__(self, msg_bus) -> None:
#         super().__init__(msg_bus)
#         self._clients: Dict[Address, Client] = {}

#     @message_type("client-list-request")
#     def get_list(self) -> Dict[Address, Client]:
#         return self._clients

#     @message_type("client-add")
#     def _client_add(self, msg) -> None:
#         content = msg["content"]
#         client: Client = Client(content["address"])
#         self._clients[content["address"]] = client

#     @message_type("client-remove")
#     def _client_rem(self, msg) -> None:
#         content = msg["content"]
#         del self._clients[content["address"]]

#     @message_type("client-authorize")
#     def _client_auth(self, msg) -> None:
#         content = msg["content"]
#         self._clients[content["address"]].auth = True
#         self._clients[content["address"]].uname = content["username"]

#     @message_type("client-unauthorize")
#     def _client_unaut(self, msg) -> None:
#         content = msg["content"]
#         self._clients[content["address"]].auth = False
#         self._clients[content["address"]].uname = ""


# if __name__ == "__main__":
#     ClientList().start()
