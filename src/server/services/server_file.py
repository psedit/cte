from typing import Dict, List
from cursor import Cursor
from piece_table import PieceTable
import os
import traceback


class ServerFile:
    def __init__(self, root: str, path: str) -> None:
        self.root: str = root
        self.path_relative: str = path
        self.pt: PieceTable
        self.cursors: Dict[str, Cursor] = {}
        self.is_saved: bool

        self.load_from_disk()

    #
    # FILESYSTEM I/O
    #

    def load_from_disk(self) -> None:
        """
        Loads the file from disk and creates the piece table object.
        """
        file_path = os.path.join(self.root, self.path_relative)
        with open(file_path) as f:
            file_list: List[str] = list(f)

        self.pt = PieceTable(file_list)
        self.is_saved = True

    def save_to_disk(self, garbage_collect=True) -> None:
        """
        Writes the current buffer to the file on disk, while keeping all
        locked pieces locked.
        """
        file_path = os.path.join(self.root, self.path_relative)

        with open(file_path, 'w') as f:
            for line in self.pt.get_lines():
                f.write(line)

        self.is_saved = True

    def change_file_path(self, new_path: str) -> None:
        self.path_relative = new_path

    #
    # LOCKS
    #

    def add_lock(self, start_piece_id: str, offset: int, length: int,
                 uname: str) -> str:
        """
        Tries to create a lock within the piece table.

        Raises ValueError if creating the lock fails.

        Returns the id of the newly locked piece.
        """
        cursor_lines = self.get_cursor_rows()
        # TODO: rollback on exception?
        lock_id = self.pt.put_piece(start_piece_id, offset, length, uname)
        try:
            self.update_cursors(cursor_lines)
        except ValueError:
            print(f"Created lock, but updating cursors failed?")
            print(traceback.format_exc())
        return lock_id

    def remove_lock(self, lock_id: str) -> None:
        self.pt.get_piece(lock_id).owner = ""

    def change_lock_owner(self, lock_id: str, uname: str) -> None:
        self.pt.get_piece(lock_id).owner = uname

    #
    # CURSORS
    #

    def move_cursor(self, uname: str, piece_id: str,
                    offset: int, column: int) -> None:
        self.cursors[uname] = Cursor(piece_id, offset, column)

    def get_cursor_list(self, exclude: List[str]) -> Dict[str, Cursor]:
        return {uname: cursor for uname, cursor in self.cursors.items()
                if uname not in exclude}

    def get_cursor_rows(self) -> Dict[str, int]:
        cursor_lines = {}
        for uname, cursor in self.cursors.items():
            cursor_lines[uname] = (self.pt.piece_to_row(cursor.piece_id)
                                   + cursor.offset)
        return cursor_lines

    def update_cursors(self, cursors) -> None:
        for uname in cursors:
            piece_id, offset = self.pt.row_to_piece(cursors[uname])
            self.cursors[uname].piece_id = piece_id
            self.cursors[uname].offset = offset

    #
    # CLIENTS
    #

    def client_join(self, uname: str) -> None:
        self.cursors[uname] = Cursor(self.pt.table[0].piece_id, 0, 0)

    def client_leave(self, uname: str) -> None:
        for piece in self.pt.table:
            if piece.owner == uname:
                piece.owner = ""

        if uname in self.cursors:
            del self.cursors[uname]

    def get_clients(self, exclude: List[str] = []) -> List[str]:
        return [uname for uname in self.cursors if uname not in exclude]

    def is_joined(self, uname: str) -> bool:
        return uname in self.cursors

    def client_count(self) -> int:
        return len(self.cursors)

    #
    # EDITS
    #

    def update_content(self, uname: str, piece_id: str, content: str) -> None:
        self.pt.set_piece_content(piece_id, content.splitlines(True))
        self.is_saved = False

    def clear_unused_pieces(self) -> None:
        cursor_lines = self.get_cursor_rows()
        self.pt.merge_unlocked_pieces()
        self.update_cursors(cursor_lines)
