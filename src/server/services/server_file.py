from typing import Any, Dict, List, Tuple, Iterable
from typedefs import Address
from piece_table import PieceTable
import os
import uuid


Cursors = Dict[Address, List[Any]]


class ServerFile:
    def __init__(self, root: str, path: str) -> None:
        self.root_dir: str = root
        self.file_path_relative: str = path
        self.file_pt: PieceTable
        # Clients and their location (piece_id, offset, column, is_idle)
        self.clients: Dict[Address, List[Any]] = {}
        # Clients and their locks (as an index), sorted by id
        self.locks: Dict[Address, List[str]] = {}
        self.lock_id_count: int = 0
        self.is_saved: bool

        self.load_from_disk()

    def load_from_disk(self) -> None:
        """
        Loads the file from disk and creates the piece table object.
        """
        file_path = os.path.join(self.root_dir, self.file_path_relative)
        with open(file_path) as f:
            file_list: List[str] = list(f)
            self.file_pt = PieceTable(file_list)
            self.is_saved = True

    def save_to_disk(self) -> None:
        """
        Writes the current buffer to the file on disk, while keeping all
        open edit-blocks open.
        """
        file_path = os.path.join(self.root_dir, self.file_path_relative)
        with open(file_path, 'w') as f:
            for line in self.file_pt.stitch():
                f.write(line)

        self.is_saved = True

    def retrieve_block(self, start: int = 0, length: int = -1) -> List[str]:
        """
        Returns all 'length' lines from line 'start', split up per line.

        A negative length will return until the last line.
        """
        return self.file_pt.get_lines(start, length)

    def process_delta(self, delta, client: Address, piece_id: str) -> None:
        """
        Writes the the delta contents (= file change) to the piece table.
        """
        # TODO: Keep locks in mind
        # TODO: Return True if succesfull
        self.is_saved = False
        pass

    def add_lock(self, client: Address,
                       piece_id: str,
                       offset: int,
                       length: int) -> str:
        """
        Tries to create the block within the piece table.
        Returns the block ID of the created block when successful, None
        otherwise
        """
        cursors_rows = self.get_cursors_rows()

        lock_id = self.file_pt.open_block(piece_id, offset, length)

        if client not in self.locks:
            self.locks[client] = [lock_id]
        else:
            self.locks[client].append(lock_id)

        self.update_cursors(cursors_rows)

        return lock_id

    def remove_lock(self, client: Address, lock_id: str) -> None:
        """
        Remove the lock if the client has access to it.
        """
        if client in self.locks and lock_id in self.locks[client]:
            self.file_pt.close_block(lock_id)
            self.locks[client].remove(lock_id)

            if not self.locks[client]:
                del self.locks[client]

    def get_lock_list(self, usernames: Dict[Address, str]) -> List[List[Any]]:
        """
        Returns a list of all locked blocks within the file, in
        the form [username of the address, piece_id].
        """
        return [[usernames[addr], lock_id] for addr in self.locks
                 for lock_id in self.locks[addr]]

    def join_file(self, client: Address) -> None:
        self.clients[client] = [self.file_pt.table[0][0], 0, 0, False]

    def move_cursor(self, client: Address,
                          piece_id: str,
                          offset: int,
                          column: int) -> None:
        self.clients[client] = [piece_id, offset, column, False]

    def get_cursor(self, client: Address) -> List[Any]:
        return self.clients[client]

    def get_cursors_rows(self) -> Dict[Address, int]:
        """
        Returns a list of the current line positions of all cursors.
        """
        cursors_rows = {}
        for client, [p_id, offset, _, _] in self.clients.items():
            cursors_rows[client] = self.file_pt.get_piece_start(p_id) + offset
        return cursors_rows

    def get_cursors(self, exclude: Iterable[Address] = ()) -> Cursors:
        c_list = self.clients.copy()
        exclude = exclude or ()
        for client in exclude:
            del c_list[client]
        return c_list

    def update_cursors(self, cursors_rows: Dict[Address, int]) -> None:
        """
        Updates the cursor dictionary to reflect piece uuid changes within
        the piece table, according to an absolute line number given as the
        argument to this function.
        """
        for address, row in cursors_rows.items():
            index, offset = self.file_pt.line_to_table_index(row)
            self.clients[address][0] = self.file_pt.table[index][0]
            self.clients[address][1] = offset

    def make_idle(self, client: Address) -> None:
        self.clients[client][-1] = False

    def drop_client(self, client: Address) -> None:
        if client in self.locks:
            client_locks = self.locks.pop(client)

            for lock in client_locks:
                self.file_pt.close_block(lock)

        del self.clients[client]

    def client_count(self) -> int:
        return len(self.clients)

    def get_clients(self, exclude: List[Address] = []) -> List[Address]:
        return [c for c in self.clients if c not in exclude]

    def is_joined(self, client) -> bool:
        return client in self.clients.keys()

    def saved_status(self) -> bool:
        return self.is_saved

    def change_file_path(self, new_path: str) -> None:
        self.file_path_relative = new_path
