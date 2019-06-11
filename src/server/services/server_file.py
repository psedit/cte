from typing import Any, Dict, List, Tuple
from client import Address
from piece_table import PieceTable
import os

Range = Tuple[int, int]


class ServerFile:
    def __init__(self, root: str, path: str) -> None:
        self.root_dir: str = root
        self.file_path_relative: str = path
        self.file_pt: PieceTable
        # Clients and their location (row, column, is_idle)
        self.clients: Dict[Address, List[Any]] = {}
        # Clients and their locks (as an index), sorted by id
        self.locks: Dict[Address, Dict[int, int]] = {}
        self.lock_id_count: int = 0
        self.is_saved: bool

        self.load_from_disk()

    def load_from_disk(self) -> None:
        """
        Loads the file from disk and creates the piece table object.
        """
        file_path = os.path.join(self.root_dir, self.file_path_relative)
        f = open(file_path)

        file_list: List[str] = list(f)
        self.file_pt = PieceTable(file_list)
        self.is_saved = True

    def save_to_disk(self) -> None:
        """
        Writes the current buffer to the file on disk, while keeping all
        open edit-blocks open.
        """
        f = open(os.path.join(self.root_dir, self.file_path_relative), 'w')
        for line in self.file_pt.stitch():
            f.write(line)

        self.is_saved = True

    def retrieve_block(self, start: int = 0, length: int = -1) -> List[str]:
        """
        Returns all 'length' lines from line 'start', split up per line.

        A negative length will return until the last line.
        """
        return self.file_pt.get_lines(start, length)

    def process_delta(self, delta) -> None:
        """
        Writes the the delta contents (= file change) to the piece table.
        """
        # TODO: Keep locks in mind
        # TODO: Return True if succesfull
        self.is_saved = False
        pass

    def add_lock(self, client: Address, start: int, length: int) -> int:
        """
        Tries to create the block within the piece table.
        Returns the block ID of the created block when successful, None
        otherwise
        """
        try:
            block_id = self.file_pt.open_block(start, length)
        except ValueError:
            return None

        if not clients in self.locks.keys():
            self.locks[client] = [block_id]
        else:
            self.locks[client].append(block_id)

        return block_id

    def remove_lock(self, client: Address, block_id: int) -> None:
        """
        Remove the lock if the client has access to it.
        """
        if client in self.locks.keys() and block_id in self.locks[client]:
            self.file_pt.close_block(block_id)
            self.locks[client].pop(block_id)

            if self.locks[client] is []:
                self.locks.pop(client)

    def move_cursor(self, client: Address, row: int, column: int) -> None:
        self.clients[client] = [row, column, True]

    def get_cursor(self, client: Address) -> List[Any]:
        return self.clients[client]

    def make_idle(self, client: Address) -> None:
        self.clients[client][2] = False

    def drop_client(self, client: Address) -> None:
        self.clients.pop(client)

    def client_count(self) -> int:
        return len(self.clients)

    def get_clients(self, exclude: List[Address] = []) -> List[Address]:
        return [c for c in self.clients.keys() if c not in exclude]

    def get_cursors(self) -> Dict[Address, List[Any]]:
        return self.clients

    def is_joined(self, client) -> bool:
        return client in self.clients.keys()

    def saved_status(self) -> bool:
        return self.is_saved
