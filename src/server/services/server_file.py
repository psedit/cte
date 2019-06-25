from typedefs import LockError
from typing import Dict, List, Tuple, Optional
from cursor import Cursor
from piece_table import PieceTable
import os


class ServerFile:
    """
    The representation of a file from the FileSystem class.
    Basically a wrapper class for PieceTable (see its respective description)
    with additional functions, of which the most important are:
    - Cursor/Client list
    - Storage of file path
    - Saving from and loading to disk functionality
    """
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

    def save_to_disk(self) -> None:
        """
        Writes the current buffer to the file on disk, but does not change the
        file representation in RAM.
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
        Tries to create a lock within the piece table, updating the cursor
        positions to the possibly newly created or changed pieces.

        Raises a LockError if creating the lock fails, and a ValueError is
        cursor repositioning fails.

        Returns the id of the newly locked piece.
        """
        cursor_lines = self.get_cursor_rows()

        try:
            lock_id = self.pt.put_piece(start_piece_id, offset, length, uname)
        except ValueError:
            raise LockError("Lock creation has failed.")

        self.update_cursors(cursor_lines)

        return lock_id

    def insert_lock_after_piece(self, piece_id: str, uname: str) -> str:
        return self.pt.put_piece_after(piece_id, uname)

    def remove_lock(self, lock_id: str) -> None:
        """
        Removes the lock in the specified piece, and merges unlocked pieces
        back into the 'orig' block at index 0. As a result, multiple pieces
        may be changed. Raises a ValueError if cursor repositioning fails.
        """
        cursor_lines = self.get_cursor_rows()

        self.pt.get_piece(lock_id).owner = ""
        self.pt.merge_unlocked_pieces()

        self.update_cursors(cursor_lines)

    def change_lock_owner(self, lock_id: str, uname: str) -> None:
        self.pt.get_piece(lock_id).owner = uname

    #
    # CURSORS
    #

    def move_cursor(self, uname: str, piece_id: str, offset: int,
                    column: int) -> Optional[Tuple[str, int, int]]:
        """
        Move the cursor of the given user to the specified position.
        Currently ignores illegal movement requests.
        """
        # Return if the piece does not exist, clamp to max lines in piece.
        try:
            piece = self.pt.get_piece(piece_id)
            offset = max(0, min(offset, piece.length - 1))
        except ValueError:
            # TODO: Raise something?
            return None

        self.cursors[uname] = Cursor(piece_id, offset, column)

        return piece.piece_id, offset, column

    def get_cursor_list(self, exclude: List[str]) -> Dict[str, Cursor]:
        return {uname: cursor for uname, cursor in self.cursors.items()
                if uname not in exclude}

    def get_cursor_rows(self) -> Dict[str, int]:
        """
        Return the cursor list in terms of row positions in the current file
        according to the piece table. Used for retaining cursor positions after
        piece table changes have been made.
        """
        cursor_lines = {}
        for uname, cursor in self.cursors.items():
            cursor_lines[uname] = (self.pt.piece_to_row(cursor.piece_id)
                                   + cursor.offset)
        return cursor_lines

    def update_cursors(self, cursors) -> None:
        """
        Updates the piece id of the given cursors based on their corresponding
        given row number. Used to restore cursor positions after piece table
        changes have been made.
        """
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
        """
        Removes the client from the file, as well as all locks which they own.
        """
        for piece in self.pt.table:
            if piece.owner == uname:
                self.remove_lock(piece.piece_id)

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
