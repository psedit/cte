from server_file import ServerFile
from typedefs import Address, LockError
from typing import Dict, List, Any
from service import Service, message_type
import traceback
import os
import shutil
import Pyro4

ERROR_WRONG_MESSAGE = 1
ERROR_FILE_NOT_IN_RAM = 2
ERROR_FILE_NOT_JOINED = 3
ERROR_FILE_NOT_PRESENT = 4
ERROR_FILE_ILLEGAL_LOCK = 5
ERROR_NOT_LOCKED = 6
ERROR_ILLEGAL_PIECE_ID = 7


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Filesystem(Service):
    """

    """
    def __init__(self, *super_args) -> None:
        super().__init__(*super_args)
        self.root_dir: str = os.path.realpath('../file_root')
        self.files: Dict[str, ServerFile] = {}

    #
    # FILE I/O
    #

    def load_file(self, file_path: str) -> None:
        """
        Add the file to the Filesystem. Path file is relative to root
        directory.
        """
        if file_path not in self.files:
            self.files[file_path] = ServerFile(self.root_dir, file_path)

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

    @message_type("file-save")
    async def _save_file_to_disk(self, msg):
        pass

    #
    # CLIENTS JOIN/LEAVE
    #

    def check_file_available(self, address: Address, username: str,
                             file_path: str) -> bool:
        if not os.path.isfile(os.path.join(self.root_dir, file_path)):
            message = f"The file {file_path} is not present on the server."
            self._send_message_client("error-response",
                                      {"message": message,
                                       "error_code": ERROR_FILE_NOT_PRESENT},
                                      address)
            return False
        return True

    def check_file_loaded(self, address: Address,
                          username: str, file_path: str) -> bool:
        if not self.check_file_available(address, username, file_path):
            return False
        elif file_path not in self.files:
            message = f"""File {file_path} is not in system RAM.
                      Join the file to load it to memory."""
            self._send_message_client("error-response",
                                      {"message": message,
                                       "error_code": ERROR_FILE_NOT_IN_RAM},
                                      address)
            return False
        return True

    def check_valid(self, address: Address,
                         uname: str, file_path: str) -> bool:
        if not self.check_file_loaded(address, uname, file_path):
            return False
        elif not self.files[file_path].is_joined(uname):
            message = f"Join the file {file_path} to gain access to it."
            self._send_message_client("error-response",
                                      {"message": message,
                                       "error_code": ERROR_FILE_NOT_JOINED},
                                      address)
            return False
        else:
            return True

    @message_type("file-join")
    async def _file_add_client(self, msg) -> None:
        """
        Add the client from the file specified in the message.
        Add the file to RAM if necessary.
        """
        content = msg["content"]
        path = content["file_path"]
        address, username = msg["sender"]

        if not self.check_file_available(address, username, path):
            return

        # Add the file to RAM if necessary.
        if path not in self.files:
            self.files[path] = ServerFile(self.root_dir, path)

        # Add the file to the client list in the ServerFile class.
        self.files[path].client_join(username)

        # Broadcast the change.
        self._send_message_client("file-join-broadcast",
                                  {"username": username,
                                   "file_path": path},
                                  *self.files[path].get_clients([username]))

    @message_type("file-leave")
    async def _file_remove_client(self, msg) -> None:
        """
        Remove the client from the file specified in the message.
        Remove the file from RAM if no clients are connected within the file.
        """
        content = msg["content"]
        path = content["file_path"]
        force = content["force_exit"]
        address, username = msg["sender"]

        if not self.check_valid(address, username, path):
            return

        # Make sure no changes are accidentally lost.
        if (not force and self.files[path].client_count() == 1
                and not self.files[path].is_saved):
            message = f"""First save the file {path} or
                      resend request with 'force_exit' = 1"""
            self._send_message_client("error-response",
                                      {"message": message,
                                       "error_code": ERROR_FILE_NOT_PRESENT},
                                      address)
            return

        self.files[path].client_leave(username)

        # Broadcast the change and remove the username
        self._send_message_client("file-leave-broadcast",
                                  {"username": username,
                                   "file_path": path},
                                  *self.files[path].get_clients())

        self._send_piece_table_change_broadcast(path)

        # Remove the file from RAM if necessary.
        if self.files[path].client_count() == 0:
            del self.files[path]

    @message_type("client-disconnect")
    async def _remove_client(self, msg) -> None:
        content = msg["content"]
        address = content["address"]
        username = content["username"]

        file_msg: Dict[str, Any] = {"sender": (address, username),
                                    "content": {"force_exit": True}}

        to_unlock = [path for path, f in self.files.items()
                     if f.is_joined(username)]

        for path in to_unlock:
            file_msg["content"]["file_path"] = path
            await self._file_remove_client(file_msg)

    #
    # CONTENT REQUEST
    #

    @message_type("file-content-request")
    async def _process_file_content_request(self, msg) -> None:
        """
        Take the file content request message and construct the appropriate
        response, sending the block via a new 'file-content-response' message.
        """
        address, username = msg["sender"]
        content = msg["content"]
        path = content["file_path"]

        if not self.check_valid(address, username, path):
            return

        file = self.files[path]
        block_list = []

        for b_id, block in file.pt.blocks.items():
            block_list.append((b_id, True, block)) # TODO: update message

        response_content = {
                             "piece_table": file.pt.table,
                             "block_list": block_list
                           }

        self._send_message_client("file-content-response",
                                  response_content,
                                  address)

    #
    # PIECE TABLE
    #

    def _send_piece_table_change_broadcast(self,
                                           file_path: str,
                                           lock_ids: List[str] = []) -> None:
        """
        Send the new table from the piece table to all clients within the file.
        Also sends the updated cursor positions.
        """
        file = self.files[file_path]

        # Due to client-side implementation, we have to send the updates one
        # by one. As a result, we also need to send an 'empty' update when
        # there where no locks given.
        for lock_id in lock_ids:
            piece = file.pt.get_piece(lock_id)

            if not piece:
                continue

            block_id = piece.block_id
            lines = file.pt.get_lines(lock_id, 0, piece.length)

            content = {
                        "file_path": file_path,
                        "piece_table": file.pt.table,
                        "changed_block": [block_id, True, lines]
                      }
            self._send_message_client("file-piece-table-change-broadcast",
                                      content,
                                      *file.get_clients())

        if not lock_ids:
            content = {
                        "file_path": file_path,
                        "piece_table": file.pt.table,
                        "changed_block": [-1, []]
                      }
            self._send_message_client("file-piece-table-change-broadcast",
                                      content,
                                      *file.get_clients())

        # Reposition all cursors in the file.
        self._broadcast_file_cursors(file_path)

    #
    # CURSORS
    #

    @message_type("cursor-move")
    async def _move_cursor(self, msg) -> None:
        address, username = msg["sender"]
        content = msg["content"]

        path = content["file_path"]
        piece_id = content["piece_id"]
        offset = content["offset"]
        column = content["column"]

        if not self.check_valid(address, username, path):
            return

        file = self.files[path]
        file.move_cursor(username, piece_id, offset, column)

        new_content = content.copy()
        new_content["username"] = username

        assert isinstance(username, str)

        self._send_message_client("cursor-move-broadcast",
                                  new_content,
                                  *file.get_clients([address]))

    def _send_cursor_list(self, file, *usernames) -> None:
        """
        Send the cursor list for a file to the given users (usernames).

        If no usernames are passed, send the cursor list to everyone who
        has joined the file.
        """
        cursors = [[uname, *cursor] for uname, cursor in file.cursors.items()]

        if not usernames:
            usernames = file.get_clients()

        self._send_message_client("cursor-list-response",
                                  {"cursor_list": cursors},
                                  *usernames)

    @message_type("cursor-list-request")
    async def _clist_request_handler(self, msg) -> None:
        address, username = msg["sender"]
        content = msg["content"]
        path = content["file_path"]

        if not self.check_valid(address, username, path):
            return

        self._send_cursor_list(self.files[path], username)

    def _broadcast_file_cursors(self, file_path: str) -> None:
        file = self.files[file_path]
        for username, cursor in file.cursors.items():
            content = {
                        "file_path": file_path,
                        "piece_id": cursor.piece_id,
                        "offset": cursor.offset,
                        "column": cursor.column,
                        "username": username
                      }
            assert isinstance(username, str)
            self._send_message_client("cursor-move-broadcast",
                                      content,
                                      *file.get_clients([username]))

    #
    # EDITS
    #

    @message_type("file-delta")
    async def _edit_block(self, msg) -> None:
        """
        Replaces a line in the given block of the piecetable
        with the new provided content.
        """

        try:
            address, username = msg["sender"]
            content = msg["content"]

            file_path = content["file_path"]
            piece_uuid = content["piece_uuid"]
            block_content = content["content"]
        except KeyError as e:
            self._send_message_client("error-response",
                                      {"message": str(e),
                                       "error_code": ERROR_WRONG_MESSAGE},
                                      address)
            return

        file = self.files[file_path]

        try:
            file.update_content(username, piece_uuid, block_content)
        except LockError as e:
            message = "Illegal edit, this lock does not belong to you."
            self._send_message_client("error-response",
                                      {"message": message,
                                       "error_code": ERROR_NOT_LOCKED},
                                      address)

            block_lines = file.pt.get_piece_content(piece_uuid)
            block_content = "".join(block_lines)

            resp_content = {
                        "file_path": file_path,
                        "piece_uuid": piece_uuid,
                        "content": block_content
                    }
            self._send_message_client("file-delta-broadcast",
                                      resp_content, address)
            return
        except ValueError as e:
            # self._send_message_client("file-delta-broadcast", content, [address])
            self._send_message_client("error-response",
                                      {"message": str(e),
                                       "error_code": ERROR_ILLEGAL_PIECE_ID},
                                      address)
            return

        self._send_message_client("file-delta-broadcast",
                                  content,
                                  *file.get_clients(exclude=[address]))

    #
    # FILES
    #

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
            for p in self.files.keys():
                if p.startswith(old_path):
                    p_new = p.replace(old_path, new_path, 1)

                    self.files[p].change_file_path(p_new)
                    self.files[p_new] = self.files[p]
                    del self.files[p]
        else:
            if old_path in self.files.keys():
                self.files[old_path].change_file_path(new_path)
                self.files[new_path] = self.files[old_path]
                del self.files[old_path]

    def _remove_file(self, old_path: str) -> None:
        """
        Removes the specified file from disk, and updates the ServerFile dict.
        """
        old_abs = os.path.join(self.root_dir, old_path)

        if self._isdir(old_path):
            shutil.rmtree(old_abs)

            for p in self.files.keys():
                if p.startswith(old_path):
                    del self.files[p]
        else:
            os.remove(old_abs)

            if old_path in self.files.keys():
                del self.files[old_path]

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

    @message_type("file-list-request")
    async def _send_file_list(self, msg) -> None:
        address = msg["sender"][0]

        root_tree = self.parse_walk(list(os.walk(self.root_dir)),
                                    self.root_dir)

        net_msg = {"root_tree": root_tree}
        self._send_message_client("file-list-response", net_msg, address)

    #
    # LOCKS
    #

    @message_type("file-lock-request")
    async def _file_add_lock(self, msg) -> None:
        """
        If possible, creates a lock in the specified file for the client,
        and sends a response with the given lock id. If locking was not
        successful, sets te 'success' flag in the response to false.
        Afterwards, broadcasts the changes to all other clients.
        """
        content = msg["content"]
        address, username = msg["sender"]

        path = content["file_path"]
        piece_id = content["piece_uuid"]
        offset = content["offset"]
        length = content["length"]

        if not self.check_valid(address, username, path):
            return self._send_lock_response(path, False, address)

        try:
            lock_id = self.files[path].add_lock(piece_id, offset,
                                                length, username)
        except ValueError as e:
            self._send_message_client("error-response",
                                      {
                                          "message": str(e),
                                          "error_code": ERROR_FILE_ILLEGAL_LOCK
                                      }, address)

            return self._send_lock_response(path, False, address)

        self._send_lock_response(path, True, address)
        self._send_piece_table_change_broadcast(path, [lock_id])
        self._broadcast_file_cursors(path)

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

        if not self.check_valid(address, username, path):
            return

        self.files[path].remove_lock(lock_id)
        self._send_piece_table_change_broadcast(path, [lock_id])


    def _send_lock_response(self, file_path: str, success: bool,
                            client: Address) -> None:
        """
        Send the file-lock-response message.
        """
        self._send_message_client("file-lock-response",
                                  {"file_path": file_path,
                                   "success": success},
                                  client)


if __name__ == "__main__":
    Filesystem.start()