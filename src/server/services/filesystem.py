from server_file import ServerFile
from typedefs import Address
from typing import Dict, List
from service import Service, message_type
import os
import shutil
import Pyro4


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Filesystem(Service):
    """

    """
    def __init__(self, *super_args) -> None:
        super().__init__(*super_args)
        # Check server config for root directory
        # TODO: retrieve from server
        self.root_dir: str = os.path.realpath('../../client')
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

        if file_path not in self.file_dict.keys():
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
        if path in self.file_dict.keys():
            return self.file_dict[path].retrieve_block(start, length)
        else:
            raise ValueError("File is not present in file system RAM.")

    @message_type("file-content-request")
    async def _process_file_content_request(self, msg) -> None:
        """
        Take the file content request message and construct the appropriate
        response, sending the block via a new 'file-content-response' message.
        """
        address = msg["sender"][0]
        content = msg["content"]

        start = content["start"]
        length = content["length"]
        file_path = content["file_path"]

        if file_path not in self.file_dict.keys():
            # TODO: send exception to client
            # "File is not in system RAM. Join the file to load it to memory."
            pass
        elif not self.file_dict[file_path].is_joined(address):
            # TODO: send exception to client
            # "Please join the file before requesting its contents."
            pass
        else:
            block = ''.join(self.get_block(file_path, start, length))

            response_content = {"file_content": block, "address": address}
            self._send_message_client("file-content-response",
                                      response_content,
                                      address)

    @message_type("file-list-request")
    async def _send_file_list(self, msg) -> None:
        address = msg["sender"][0]

        net_msg = {
            "root_tree": self.root_tree
        }

        print("Je bent een plakje kaas.")

        self._send_message_client("file-list-response", net_msg, address)

    @message_type("cursor-move")
    async def _move_cursor(self, msg) -> None:
        address, username = msg["sender"]
        content = msg["content"]

        path = content["file_path"]
        row = content["row"]
        column = content["column"]

        file = self.file_dict[path]

        if not file.is_joined(address):
            # TODO: send exception to client
            # "Please join the file first before moving within it."
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
    async def _send_cursor_list(self, msg):
        address = msg["sender"][0]
        content = msg["content"]

        path = content["file_path"]

        # if not file.is_joined(address):
        # TODO: send exception to client
        # "Please join the file first before requesting cursor locations."
        # return

        curs_f = self.file_dict[path].get_cursors()
        cursors = [[self.usernames[c]] + curs_f[c] for c in curs_f.keys()]

        self._send_message_client("cursor-list-response",
                                  {"cursor_list": cursors},
                                  address)

    @message_type("file-join")
    async def _file_add_client(self, msg) -> None:
        """
        Add the client from the file specified in the message.
        Add the file to RAM if necessary.
        """
        content = msg["content"]

        file = content["file_path"]
        address, username = msg["sender"]

        # TODO: this should go via the database
        self.usernames[address] = username

        if not os.path.isfile(os.path.join(self.root_dir, file)):
            # TODO: send exception to client
            # "This file is not present on the server."
            return

        # Add the file to RAM if necessary.
        if file not in self.file_dict.keys():
            self.file_dict[file] = ServerFile(self.root_dir, file)

        # Add the file to the client list in the ServerFile class.
        self.file_dict[file].move_cursor(address, 0, 0)

    @message_type("file-leave")
    async def _file_remove_client(self, msg) -> None:
        """
        Remove the client from the file specified in the message.
        Remove the file from RAM if no clients are connected within the file.
        """
        content = msg["content"]

        file = content["file_path"]
        force = content["force_exit"]
        address = msg["sender"][0]

        if (not force and self.file_dict[file].client_count() == 1
                and self.file_dict[file].saved_status() is False):
            # TODO: send exception to client NOTE: this could also be done
            # client side:
            # "First save the file or resend request with force_exit = 1"
            return

        self.file_dict[file].drop_client(address)

        # Remove the file from RAM if necessary.
        if self.file_dict[file].client_count() == 0:
            self.file_dict.pop(file)

    def _isdir(self, path: str) -> bool:
        """
        Checks if the given path is a directory, although it does not
        necessarily need to have been created yet.
        """
        # Would use os.path.isdir, but that checks whether the path
        # actually exists, rather than whether it would be a directory
        # if it existed.
        return f"{os.path.dirname(path)}{os.sep}" == path

    def _rename_file(self, old_path: str, new_path: str) -> None:
        """
        Renames the file or directory 'old_path' to 'new_path', both paths
        relative to the root directory. Also updates ServerFile classes and
        dictionary in case they are currently in memory.
        """
        old_abs = os.path.join(self.root_dir, old_path)
        new_abs = os.path.join(self.root_dir, new_path)

        os.makedirs(os.path.dirname(new_abs), exist_ok=True)
        os.rename(old_abs, new_abs)

        # Update the file paths within memory.
        if self._isdir(old_path):
            for p in self.file_dict.keys():
                if p.startswith(old_path):
                    p_new = p.replace(old_path, new_path, 1)

                    self.file_dict[p].change_file_path(p_new)
                    self.file_dict[p_new] = self.file_dict[p]
                    del self.file_dict[p]
        else:
            if old_path in self.file_dict.keys():
                self.file_dict[old_path].change_file_path(new_path)
                self.file_dict[new_path] = self.file_dict[old_path]
                del self.file_dict[old_path]

    def _remove_file(self, old_path: str) -> None:
        """
        Removes the specified file from disk, and updates the ServerFile dict.
        """
        old_abs = os.path.join(self.root_dir, old_path)

        if self._isdir(old_path):
            shutil.rmtree(old_abs)

            for p in self.file_dict.keys():
                if p.startswith(old_path):
                    del self.file_dict[p]
        else:
            os.remove(old_abs)

            if old_path in self.file_dict.keys():
                del self.file_dict[old_path]

    def _add_file(self, new_path: str, file_content: str) -> None:
        """
        Create the specified file and required directories on disk, with the
        given file contents.
        """
        new_abs = os.path.join(self.root_dir, new_path)

        os.makedirs(os.path.dirname(new_abs), exist_ok=True)

        if not self._isdir(new_path):
            with open(new_abs, 'w') as f:
                f.write(file_content)

    @message_type("file-change")
    async def _change_file(self, msg):
        """
        Creates the file in the server root directory.
        Overwrites file if it is already present.
        """
        content = msg["content"]
        # address = msg["sender"]
        old_path = content["old_path"]
        new_path = content["new_path"]

        if new_path and old_path:
            self._rename_file(old_path, new_path)
        elif old_path:
            self._remove_file(old_path)
        elif new_path:
            self._add_file(new_path, content["file_content"])

        self.root_tree = self.parse_walk(list(os.walk(self.root_dir)),
                                         self.root_dir)

        c_msg = self._send_message("client-list-request", {})
        resp = await self._wait_for_response(c_msg["uuid"])

        self._send_message_client("file-change-broadcast", content,
                                  *resp["content"]["client_list"])


if __name__ == "__main__":
    Filesystem.start()
