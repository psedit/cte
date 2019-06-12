from server_file import ServerFile
from typedefs import Address
from typing import Dict, List
from service import Service, message_type
import os
import Pyro4


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Filesystem(Service):
    """

    """
    def __init__(self, msg_bus) -> None:
        super().__init__(msg_bus)
        # Check server config for root directory
        # TODO: retrieve from server
        self.root_dir: str = os.path.realpath('../test/')
        self.usernames: Dict[Address, str] = {}

        # Files sorted by path relative to root dir
        self.file_dict: Dict[str, ServerFile] = {}
        self.root_tree = self.parse_walk(list(os.walk(self.root_dir)),
                                         self.root_dir)

    def add_file(self, file_path: str) -> None:
        """
        Add the file to the Filesystem. Path file is relative to root
        directory.
        """

        if file_path not in self.file_dict:
            self.file_dict[file_path] = ServerFile(self.root_dir, file_path)

    def list_files(self) -> List[str]:
        """
        Lists all files currently within the file system (in RAM), relative to
        the root directory.
        """
        return list(self.file_dict.keys())

    def parse_walk(self, walk, path):
        """
        Creates directory tree of the root directory.
        """
        dir_tup = [t for t in walk if t[0] == path][0]
        walk.remove(dir_tup)
        tree = []

        for dir_name in dir_tup[1]:
            tree.append((dir_name,
                         self.parse_walk(walk, os.path.join(path, dir_name))))
        for file_name in dir_tup[2]:
            tree.append(file_name)

        return tree

    def get_block(self,
                  path: str,
                  start: int = 0,
                  length: int = -1) -> List[str]:
        """
        Returns all 'length' lines starting from 'start', of the specified file
        within the file system.

        Keyword arguments:
        path -- Path to the file relative to the root directory.
        start -- Line number indicating start position
        length -- Amount of lines to return, -1 indicates until the last line.
        """
        if path in self.file_dict:
            return self.file_dict[path].retrieve_block(start, length)
        else:
            raise ValueError("File is not present in file system RAM.")

    def _is_joined(self, address, file_path) -> bool:
        if file_path not in self.file_dict:
            # TODO: send exception to client
            # "File is not in system RAM. Join the file to load it to memory."
            return False
        elif not self.file_dict[file_path].is_joined(address):
            # TODO: send exception to client
            # "Please join the file before requesting its contents."
            return False
        else:
            return True

    @message_type("file-content-request")
    def _process_file_content_request(self, msg) -> None:
        """
        Take the file content request message and construct the appropriate
        response, sending the block via a new 'file-content-response' message.
        """
        address = msg["sender"][0]
        content = msg["content"]

        start = content["start"]
        length = content["length"]
        file_path = content["file_path"]

        if self._is_joined(address, file_path):
            block = self.get_block(file_path, start, length)

            response_content = {"file_content": block, "address": address}
            self._send_message_client("file-content-response",
                                      response_content,
                                      address)

    @message_type("file-list-request")
    def _send_file_list(self, msg) -> None:
        content = msg["content"]
        address = msg["sender"][0]

        net_msg = {
            "root_tree": self.root_tree
        }

        self._send_message_client("file-list-response", net_msg, address)

    @message_type("cursor-move")
    def _move_cursor(self, msg) -> None:
        address, username = msg["sender"]
        content = msg["content"]

        path = content["file_path"]
        row = content["row"]
        column = content["column"]

        file = self.file_dict[path]

        if not self._is_joined(address, path):
            return

        file.move_cursor(address, row, column)

        new_content = {
                "username": username,
                "file_path": path,
                "row": row,
                "column": column
            }

        self._send_message_client("cursor-move-broadcast",
                                  new_content,
                                  *file.get_clients(exclude=[address]))

    @message_type("cursor-list-request")
    def _send_cursor_list(self, msg):
        address = msg["sender"][0]
        content = msg["content"]

        path = content["file_path"]

        if not self._is_joined(address, path):
            # TODO: send exception to client
            # "Please join the file first before requesting cursor locations."
            return

        curs_f = self.file_dict[path].get_cursors()
        cursors = [[self.usernames[c]] + curs_f[c] for c in curs_f]

        self._send_message_client("cursor-list-response",
                                  {"cursor_list": cursors},
                                  address)

    @message_type("file-join")
    def _file_add_client(self, msg) -> None:
        """
        Add the client from the file specified in the message.
        Add the file to RAM if necessary.
        """
        content = msg["content"]

        path = content["file_path"]
        address, username = msg["sender"]

        # TODO: this should go via the pyro
        self.usernames[address] = username

        if not os.path.isfile(os.path.join(self.root_dir, path)):
            # TODO: send exception to client
            # "This file is not present on the server."
            return

        # Add the file to RAM if necessary.
        if path not in self.file_dict:
            self.file_dict[path] = ServerFile(self.root_dir, path)

        # Add the file to the client list in the ServerFile class.
        self.file_dict[path].move_cursor(address, 0, 0)

    @message_type("file-leave")
    def _file_remove_client(self, msg) -> None:
        """
        Remove the client from the file specified in the message.
        Remove the file from RAM if no clients are connected within the file.
        """
        content = msg["content"]

        path = content["file_path"]
        force = content["force_exit"]
        address = msg["sender"][0]

        if path not in self.file_dict:
            return

        if (not force and self.file_dict[path].client_count() == 1
                and self.file_dict[path].saved_status() is False):
            # TODO: send exception to client
            # "First save the file or resend request with force_exit = 1"
            return

        self.file_dict[path].drop_client(address)

        # Remove the file from RAM if necessary.
        if self.file_dict[file].client_count() == 0:
            del self.file_dict[path]

    @message_type("file-lock-request")
    def _file_add_lock(self, msg) -> None:
        """
        If possible, creates a lock in the specified file for the client,
        and sends a response with the give lock id. If locking was not
        successful, sets te 'success' flag in the response to false.
        Afterwards, broadcasts the changes to all other clients.
        """
        content = msg["content"]
        address, username = msg["sender"]

        path = content["file_path"]
        start = content["start"]
        length = content["length"]

        if not self._is_joined(address, path):
            self._send_lock_response(path, False, 0, address)
            return

        block_id = self.file_dict[path].add_lock(address, start, length)

        if block_id is None:
            _send_lock_response(path, False, 0, address)
        else:
            self._send_lock_response(path, True, block_id, address)
            self._send_lock_broadcast(username, block_id, True, path,
                                      start, length, address)

    @message_type("file-unlock-request")
    def _file_remove_lock(self, msg) -> None:
        """
        Remove the client's lock from the specified file, and broadcasts
        the changes to all other clients.
        """
        content = msg["content"]
        address, username = msg["sender"]

        path = content["file_path"]
        block_id = content["lock_id"]

        if not self._is_joined(address, path):
            return

        self.file_dict[path].remove_lock(address, block_id)

        self._send_lock_broadcast(username, block_id, False, path,
                                  0, 0, address)

    def _send_lock_response(self, file_path: str, success: bool,
                            lock_id: int, client: Address) -> None:
        """
        Send the curser-lock-response message.
        """
        self._send_message_client("file-lock-response",
                                  { "file_path": file_path,
                                    "success": success,
                                    "lock_id": lock_id },
                                  client)

    def _send_lock_broadcast(self, username: str, lock_id: int, locked: bool,
                             file_path: str, start: int, length: int,
                             excl: Address) -> None:
        """
        Send the curser-lock-change-broadcast message to all clients within
        the file.
        """
        file_path = self.file_dict[file_path]

        content = { "username": username,
                    "lock_id": id,
                    "is_locked": locked,
                    "file_path": file_path,
                    "start": start,
                    "length": lock_id }

        self._send_message_client("file-lock-change-broadcast", content,
                                  *file.get_clients(exclude=[excl]))

    @message_type("file-lock-list-request")
    def _file_send_lock_list(self, msg) -> None:
        """
        Sends the lock list of the specified file to the client that
        requests it.
        """
        content = msg["content"]
        address, username = msg["sender"]

        path = content["file_path"]

        if not self._is_joined(address, path):
            # TODO: send exception
            return

        print(self.usernames)
        lock_list = self.file_dict[path].get_lock_list(self.usernames)
        self._send_message_client("file-lock-list-response",
                                  {"file_path": path,
                                   "lock_list": lock_list},
                                  address)

if __name__ == "__main__":
    Filesystem.start()
