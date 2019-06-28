from .server_file import ServerFile
from .typedefs import Address, LockError
from .service import Service, message_type
from typing import Dict, List
import base64
import tarfile
import os
import shutil
import Pyro4

# TODO: dit is vast lelijk
ERROR_WRONG_MESSAGE = 1
ERROR_FILE_NOT_IN_RAM = 2
ERROR_FILE_NOT_JOINED = 3
ERROR_FILE_NOT_PRESENT = 4
ERROR_FILE_ILLEGAL_LOCK = 5
ERROR_NOT_LOCKED = 6
ERROR_ILLEGAL_PIECE_ID = 7
ERROR_FILE_NOT_SAVED = 8


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Filesystem(Service):
    """
    Main file system service. Keeps track of all files currently in the system
    and in memory. The main functionality is handling messages from the other
    services, and provided to appropriate responses and broadcasts to the
    connected clients.

    Files are in the form of ServerFile classes. For more information,
    see server_file.py.

    The functionality listed:
    - The current working directory can be requested, with which clients can
      select the available files;
    - Clients can (and are required to) join specific files to gain access to
      its contents and functions ;
    - Cursor locations are stored and broadcasted to users;
    - Clients can request locks in files, and
    - Clients can update the file content in their locks;
    - Clients can add, remove or rename files;
    - Clients can download all files on the server.

    For the full  message descriptions, see the wiki over at github
    (https://github.com/psedit/cte/wiki/Server-service-messages)
    """
    def __init__(self, *super_args) -> None:
        super().__init__(*super_args)
        # Check server config for root directory
        # TODO: retrieve from server
        self.root_dir: str = os.path.realpath('file_root')
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir, exist_ok=True)
        files: Dict[str, ServerFile] = {}

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
        file_path = msg["content"]["file_path"]
        username = msg["sender"][1]

        file = self.files[file_path]
        lines = file.save_to_disk()  # noqa

        self._send_message_client("file-save-broadcast",
                                  {
                                      "file_path": file_path,
                                      "username": username
                                  },
                                  *file.get_clients())

    @message_type("file-project-request")
    async def _send_files_as_tar(self, msg):
        """
        Sends the complete root directory currently on disk to the requesting
        client. The files are encoded in base64 as a tar file.
        """
        addr = msg["sender"][0]

        with tarfile.open(".project.tar", "w|") as tar:
            tar.add(self.root_dir, arcname=os.path.basename(self.root_dir))
        with open(".project.tar", 'rb') as f:
            b64_string = base64.b64encode(f.read()).decode('utf-8')

        self._send_message_client("file-project-response",
                                  {"data": b64_string},
                                  addr)

        os.remove(".project.tar")

    @message_type("file-folder-upload")
    async def _upload_folder_as_tar(self, msg):
        """
        Creates a folder with content based on a given base64 byte stream
        """
        b64_string = msg["content"]["data"]
        data_bytes = base64.b64decode(b64_string)

        with open(".project.tar", "wb") as f:
            f.write(data_bytes)
        with tarfile.open(".project.tar", "r|") as tar:
            tar.extractall(path=self.root_dir)

        os.remove(".project.tar")

        root_tree = self.parse_walk(list(os.walk(self.root_dir)),
                                    self.root_dir)

        c_msg = self._send_message("client-list-request", {})
        resp = await self._wait_for_response(c_msg["uuid"])

        self._send_message_client("file-list-broadcast",
                                  {
                                      "root_tree": root_tree
                                  },
                                  *resp["content"]["client_list"])

    #
    # CLIENTS JOIN/LEAVE
    #

    def check_file_available(self, address: Address, file_path: str) -> bool:
        """
        Checks whether the file is present in the root directory, and warn
        the client when it is not.
        """
        if not os.path.isfile(os.path.join(self.root_dir, file_path)):
            message = f"The file {file_path} is not present on the server."
            self._send_message_client("error-response",
                                      {"message": message,
                                       "error_code": ERROR_FILE_NOT_PRESENT},
                                      address)
            return False
        return True

    def check_file_loaded(self, address: Address, file_path: str) -> bool:
        """
        After checking whether the file is present on disk, checks whether the
        file is present in server RAM. Warn the client when it is not.
        """
        if not self.check_file_available(address, file_path):
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

    def check_valid(self, address: Address, uname: str, file_path: str) -> bool:  # noqa
        """
        Check whether the client has joined the file, as well as if the file
        is loaded correctly. Warns the client when this is not the case.

        This function needs to be called before handling most file-specific
        messages.
        """
        if not self.check_file_loaded(address, file_path):
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

        if not self.check_file_available(address, path):
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
    async def _file_client_leave(self, msg) -> None:
        """
        Remove the client from the file specified in the message, as well as
        its locks. Remove the file from RAM if no clients are connected within
        the file.
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
            message = (f"First save the file {path} or resend request"
                       f"with 'force_exit' = true")
            self._send_message_client("error-response",
                                      {"message": message,
                                       "error_code": ERROR_FILE_NOT_SAVED},
                                      address)
            return

        self._file_remove_client(address, username, path, force)

    @message_type("client-disconnect")
    async def _remove_client(self, msg) -> None:
        """
        Removes the clients from all files it was present in. Same as
        'file-leave' handler for every file.
        """
        content = msg["content"]

        address = content["address"]
        username = content["username"]

        to_unlock = [path for path, f in self.files.items()
                     if f.is_joined(username)]

        for path in to_unlock:
            self._file_remove_client(address, username, path, True)

    def _file_remove_client(self, addr: Address, username: str,
                            path: str, force: bool) -> None:
        """
        Removes the specified client from the specified file, removing all
        locks in the process.

        Because of this, the piece table of the file is updated as well as the
        cursor positions. These changes are broadcasted to the other clients.
        """
        file = self.files[path]

        file.client_leave(username)

        # Broadcast the change and remove the username
        self._send_message_client("file-leave-broadcast",
                                  {"username": username,
                                   "file_path": path},
                                  *file.get_clients(exclude=[username]))

        self._update_and_broadcast_piece_table(path, update_orig=True)
        self._broadcast_file_cursors(path)

        # Remove the file from RAM if necessary.
        if file.client_count() == 0:
            del self.files[path]

    #
    # CONTENT REQUEST
    #

    @message_type("file-content-request")
    async def _process_file_content_request(self, msg) -> None:
        """
        Constructs and sends the file content message to the requesting client,
        sending the complete piece table and the block contents within.
        """
        content = msg["content"]
        address, username = msg["sender"]
        path = content["file_path"]

        if not self.check_valid(address, username, path):
            return

        file = self.files[path]
        block_list = []

        for b_id, block in file.pt.blocks.items():
            block_list.append((b_id, True, block))  # TODO: update message

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

    def _update_and_broadcast_piece_table(self,
                                          file_path: str,
                                          piece_ids: List[str] = [],
                                          update_orig: bool = False) -> None:
        """
        Sends the current piece table to all clients within the file, as well
        as the updated blocks within the table.

        'piece_ids' is a list of pieces of which their blocks have been added
        or updated. Used when a lock is added for instance.

        The value of 'update_orig' indicates whether the block at index 0,
        the 'orig' block, should be re-send to the clients. Used when a lock
        is removed, and old unlocked blocks are merged into 'orig'.
        """
        file = self.files[file_path]
        changed_blocks = []

        # Update the 'orig' content after merging unlocked blocks into it.
        if update_orig:
            changed_blocks.append([0, False, file.pt.blocks[0]])

        # Go through the given updated block_id's, and construct the message.
        for piece_id in piece_ids:
            piece = file.pt.get_piece(piece_id)
            lines = file.pt.get_piece_content(piece_id)

            changed_blocks.append([piece.block_id, False, lines])

        # Clear the unused blocks in the table and add this to the broadcast.
        removed_blocks = file.pt.clear_unused_blocks()
        changed_blocks.extend([[b_id, True, []] for b_id in removed_blocks])

        # Broadcast the change to all clients within the file.
        content = {
                    "file_path": file_path,
                    "piece_table": file.pt.table,
                    "changed_blocks": changed_blocks
                  }
        self._send_message_client("file-piece-table-change-broadcast",
                                  content,
                                  *file.get_clients())

    #
    # CURSORS
    #

    @message_type("cursor-move")
    async def _move_cursor(self, msg) -> None:
        """
        Moves the client that has send the message to the specified location
        within the piece table. Broadcasts this change to the other clients
        """
        address, username = msg["sender"]
        content = msg["content"]

        path = content["file_path"]
        piece_id = content["piece_id"]
        offset = content["offset"]
        column = content["column"]

        if not self.check_valid(address, username, path):
            return

        file = self.files[path]

        result = file.move_cursor(username, piece_id, offset, column)
        if result is None:
            return
        _, offset, column = result

        new_content = content.copy()
        new_content.update({"username": username,
                            "offset": offset,
                            "column": column})

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
        """
        Sends the cursor list to the requesting client.
        """
        address, username = msg["sender"]
        content = msg["content"]
        path = content["file_path"]

        if not self.check_valid(address, username, path):
            return

        self._send_cursor_list(self.files[path], username)

    def _broadcast_file_cursors(self, file_path: str) -> None:
        """
        Broadcast the cursor locations of every client to all other clients.
        """
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
        Replaces a line in the given block of the piecetable with the new
        provided content.
        """
        content = msg["content"]
        address, username = msg["sender"]

        file_path = content["file_path"]
        piece_uuid = content["piece_uuid"]
        block_content = content["content"]

        file = self.files[file_path]

        try:
            file.update_content(username, piece_uuid, block_content)
        except LockError:
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
            files_new = {}
            for p in self.files:
                if p.startswith(old_path):
                    p_new = p.replace(old_path, new_path, 1)

                    self.files[p].change_file_path(p_new)
                    self.files[p_new] = self.files[p]
                else:
                    files_new[p] = self.files[p]

            self.files = files_new
        else:
            if old_path in self.files:
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

            files_new = {}
            for p in self.files:
                if not p.startswith(old_path):
                    files_new[p] = self.files[p]
            self.files = files_new
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
        Process the file-change message, by calling either _remove_file,
        _add_file or _rename_file. Also broadcast the change to the clients.
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
        """
        Send the file list back to the requesting client.
        """
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
        successful, sets the 'success' flag in the response to false.
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


        prev_table = str(self.files[path].pt)
        prev_cursors = str(self.files[path].cursors)

        try:
            lock_id = self.files[path].add_lock(piece_id, offset,
                                                length, username)
        except LockError:
            message = f"Lock creation in {path} has failed."
            self._send_message_client("error-response",
                                      {
                                          "message": message,
                                          "error_code": ERROR_FILE_ILLEGAL_LOCK
                                      }, address)

            return self._send_lock_response(path, False, address)
        except ValueError as e:
            self._error("Cursor repositioning has failed, possible table "
                        "divergence at the client side.")
            return

        self._send_lock_response(path, True, address)
        self._update_and_broadcast_piece_table(path, [lock_id])
        self._broadcast_file_cursors(path)

    @message_type("file-lock-insert-request")
    async def _file_insert_lock(self, msg) -> None:
        """
        Insert a new lock after the given piece_uuid, or at the beginning of
        the file if piece_uuid = "". Broadcasts this table change to all
        clients.
        """
        content = msg["content"]
        address, uname = msg["sender"]

        path = content["file_path"]
        piece_id = content["piece_uuid"]

        try:
            lock_id = self.files[path].insert_lock_after_piece(piece_id, uname)
            self._update_and_broadcast_piece_table(path, [lock_id])
        except ValueError as e:
            self._send_message_client("error-response",
                                      {
                                          "message": str(e),
                                          "error_code": ERROR_FILE_ILLEGAL_LOCK
                                      }, address)

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

        try:
            self.files[path].remove_lock(lock_id)
        except ValueError:
            self._error("Cursor repositioning has failed, possible table "
                        "divergence at the client side.")

        self._update_and_broadcast_piece_table(path, update_orig=True)
        self._broadcast_file_cursors(path)

    def _send_lock_response(self, file_path: str, success: bool,
                            client: Address) -> None:
        """
        Send the file-lock-response message, which indicates whether the
        locking was successful.
        """
        self._send_message_client("file-lock-response",
                                  {"file_path": file_path,
                                   "success": success},
                                  client)


def main():
    Filesystem.start()


if __name__ == "__main__":
    main()
