from server_file import ServerFile
from typedefs import Address
from typing import Dict, List
from service import Service, message_type
import os
import shutil
import Pyro4

# TODO: dit is vast lelijk
ERROR_FILE_NOT_IN_RAM = 1
ERROR_FILE_NOT_JOINED = 2
ERROR_FILE_NOT_PRESENT = 3
ERROR_FILE_ILLEGAL_LOCK = 4


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Filesystem(Service):
    """

    """
    def __init__(self, *super_args) -> None:
        super().__init__(*super_args)
        # Check server config for root directory
        # TODO: retrieve from server
        self.root_dir: str = os.path.realpath('../test')
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

    def _is_joined(self, address, file_path) -> bool:
        if file_path not in self.file_dict:
            message = f"""File {file_path} is not in system RAM.
                      Join the file to load it to memory."""
            self._send_message_client("error-response",
                                      {"message": message,
                                       "error_code": ERROR_FILE_NOT_IN_RAM},
                                      address)
            return False
        elif not self.file_dict[file_path].is_joined(address):
            message = f"Join the file {file_path} to gain access to it."
            self._send_message_client("error-response",
                                      {"message": message,
                                       "error_code": ERROR_FILE_NOT_JOINED},
                                      address)
            return False
        else:
            return True

    def _extend_pt_uname(self, file):
        """
        Returns an extended piece table including usernames of piece owners.
        """
        ex_tab = []
        for i, piece in enumerate(file.file_pt.table):
            uname = self.usernames.get(file.get_lock_client(piece[0])) or ""
            ex_tab.append([*piece, uname])
        return ex_tab

    @message_type("file-content-request")
    async def _process_file_content_request(self, msg) -> None:
        """
        Take the file content request message and construct the appropriate
        response, sending the block via a new 'file-content-response' message.
        """
        address = msg["sender"][0]
        content = msg["content"]

        file_path = content["file_path"]

        if self._is_joined(address, file_path):
            file = self.file_dict[file_path]
            block_list = []

            for b_id, block in file.file_pt.blocks.items():
                block_list.append((b_id, block.is_open(), block.lines))

            response_content = {"piece_table": self._extend_pt_uname(file),
                                "block_list": block_list}

            self._send_message_client("file-content-response",
                                      response_content,
                                      address)
        else:
            pass
            # File not joined error

    @message_type("file-list-request")
    async def _send_file_list(self, msg) -> None:
        address = msg["sender"][0]

        net_msg = {"root_tree": self.root_tree}
        self._send_message_client("file-list-response", net_msg, address)

    @message_type("cursor-move")
    async def _move_cursor(self, msg) -> None:
        address, username = msg["sender"]
        content = msg["content"]

        path = content["file_path"]
        piece_id = content["piece_id"]
        offset = content["offset"]
        column = content["column"]

        file = self.file_dict[path]

        if not self._is_joined(address, path):
            return

        file.move_cursor(address, piece_id, offset, column)

        new_content = {
                "username": username,
                "file_path": path,
                "piece_id": piece_id,
                "offset": offset,
                "column": column,
            }

        self._send_message_client("cursor-move-broadcast",
                                  new_content,
                                  *file.get_clients(exclude=[address]))

    @message_type("cursor-list-request")
    async def _send_cursor_list(self, msg):
        address = msg["sender"][0]
        content = msg["content"]

        path = content["file_path"]

        if not self._is_joined(address, path):
            return

        curs_f = self.file_dict[path].get_cursors([address])
        cursors = [[self.usernames[c]] + curs_f[c] for c in curs_f]

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

        path = content["file_path"]
        address, username = msg["sender"]

        # TODO: this should go via the pyro
        self.usernames[address] = username

        if not os.path.isfile(os.path.join(self.root_dir, path)):
            message = f"The file {path} is not present on the server."
            self._send_message_client("error-response",
                                      {"message": message,
                                       "error_code": ERROR_FILE_NOT_PRESENT},
                                      address)
            return

        # Add the file to RAM if necessary.
        if path not in self.file_dict:
            self.file_dict[path] = ServerFile(self.root_dir, path)

        # Add the file to the client list in the ServerFile class.
        self.file_dict[path].join_file(address)

        # Broadcast the change.
        self._send_file_join_broadcast(path, address)

    @message_type("file-leave")
    async def _file_remove_client(self, msg) -> None:
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
            message = f"""First save the file {path} or
                      resend request with 'force_exit' = 1"""
            self._send_message_client("error-response",
                                      {"message": message,
                                       "error_code": ERROR_FILE_NOT_PRESENT},
                                      address)
            return

        self.file_dict[path].drop_client(address)

        # Remove the file from RAM if necessary.
        if self.file_dict[path].client_count() == 0:
            del self.file_dict[path]

        # Broadcast the change and remove the username
        self._send_file_leave_broadcast(path, address)
        del self.usernames[address]

    @message_type("client-disconnect")
    async def _remove_client(self, msg) -> None:
        content = msg["content"]

        address = content["address"]

        for path, f in self.file_dict.items():
            if f.is_joined(address):
                f.drop_client(address)
                self._send_file_leave_broadcast(path, address)

        # Broadcast the change and remove the username
        if address in self.usernames:
            self._send_file_leave_broadcast(path, address)
            del self.usernames[address]

    def _send_file_join_broadcast(self, file_path: str, client: Address):
        file = self.file_dict[file_path]
        self._send_message_client("file-join-broadcast",
                                  {"username": self.usernames[client],
                                   "file_path": file_path},
                                  *file.get_clients(exclude=[client]))

    def _send_file_leave_broadcast(self, file_path: str, client: Address):
        file = self.file_dict[file_path]
        self._send_message_client("file-leave-broadcast",
                                  {"username": self.usernames[client],
                                   "file_path": file_path},
                                  *file.get_clients(exclude=[client]))

    @message_type("file-lock-request")
    async def _file_add_lock(self, msg) -> None:
        """
        If possible, creates a lock in the specified file for the client,
        and sends a response with the give lock id. If locking was not
        successful, sets te 'success' flag in the response to false.
        Afterwards, broadcasts the changes to all other clients.
        """
        content = msg["content"]
        address, username = msg["sender"]

        path = content["file_path"]
        piece_id = content["piece_uuid"]
        offset = content["offset"]
        length = content["length"]

        if not self._is_joined(address, path):
            self._send_lock_response(path, False, "", address)
            return

        try:
            lock_id = self.file_dict[path].add_lock(address, piece_id,
                                                    offset, length)
        except ValueError as e:
            self._send_message_client("error-response",
                                      {
                                          "message": str(e),
                                          "error_code": ERROR_FILE_ILLEGAL_LOCK
                                      },
                                      address)

            self._send_lock_response(path, False, "", address)
            return

        self._send_lock_response(path, True, lock_id, address)
        self._send_piece_table_change_broadcast(path, lock_id, True)

    @message_type("file-unlock-request")
    async def _file_remove_lock(self, msg) -> None:
        """
        Remove the client's lock from the specified file, and broadcasts
        the changes to all other clients.
        """
        content = msg["content"]
        address, username = msg["sender"]

        path = content["file_path"]
        lock_id = content["lock_id"]

        if not self._is_joined(address, path):
            return

        self.file_dict[path].remove_lock(address, lock_id)
        self._send_piece_table_change_broadcast(path, lock_id, False)

    def _send_lock_response(self, file_path: str, success: bool,
                            lock_id: str, client: Address) -> None:
        """
        Send the file-lock-response message.
        """
        self._send_message_client("file-lock-response",
                                  {"file_path": file_path,
                                   "success": success,
                                   "lock_id": lock_id},
                                  client)

    def _send_piece_table_change_broadcast(self,
                                           file_path: str,
                                           lock_id: str,
                                           is_locked: bool) -> None:
        """
        Send the new table from the piece table to all clients within the file.
        """
        file = self.file_dict[file_path]

        lines = file.file_pt.get_piece_content(lock_id)
        block_id = file.file_pt.get_piece_block_id(lock_id)
        content = {
                    "file_path": file_path,
                    "piece_table": self._extend_pt_uname(file),
                    "changed_block": [block_id, is_locked, lines]
                  }
        self._send_message_client("file-piece-table-change-broadcast", content,
                                  *file.get_clients())

        self._send_cursor_list(file_path, *file.get_clients())

    @message_type("file-lock-list-request")
    async def _file_send_lock_list(self, msg) -> None:
        """
        Sends the lock list of the specified file to the client that
        requests it.
        """
        content = msg["content"]
        address, username = msg["sender"]

        path = content["file_path"]

        if not self._is_joined(address, path):
            return

        lock_list = self.file_dict[path].get_lock_list(self.usernames)
        self._send_message_client("file-lock-list-response",
                                  {"file_path": path,
                                   "lock_list": lock_list},
                                  address)

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
