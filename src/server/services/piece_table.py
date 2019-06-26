from typing import List, Tuple, Dict, Union
import uuid
from piece import Piece
from typedefs import LockError


class PieceTable:
    """
    Text file data structure consisting of the original file together with
    so-called "blocks", for which a table is used to couple these seperate
    blocks into one single file. The table contains 'pieces' which refer to
    subsections of blocks (using a block id) and have an uuid and owner.

    Pieces can can be created on top of the original file and locked, such
    that no other pieces can be created on top of them, until the
    piece is unlocked manually. Blocks can thereafter be edited, while the
    piece table makes sure the general structure stays intact.
    """
    def __init__(self, text) -> None:
        """
        Initialises the block dictionary and piece table. Also creates the
        block with id 0, the 'orig' block which contains the original file.
        """
        if not text:
            text = ["\n"]

        lines = self.text_to_lines(text)
        orig = Piece(str(uuid.uuid4()), 0, 0, len(lines), "")

        self.blocks: Dict[int, List[str]] = {0: lines}
        self.table: List[Piece] = [orig]

    @staticmethod
    def text_to_lines(text) -> List[str]:
        return text.splitlines(True) if isinstance(text, str) else text

    def __len__(self) -> int:
        """
        Returns the length of the stitched file according to the piece table.
        """
        return sum(piece.length for piece in self.table)

    def __str__(self) -> str:
        """
        Prints the piece table in an easily readable manner.
        """
        fmt = "{:>38}" + "{:>10}"*3 + "{:>15}" + "{:>10}"
        str_table = fmt.format("Piece ID", "Block ID", "Start",
                               "Length", "Owner", "Locked") + "\n"

        for p in self.table:
            str_table += fmt.format(*p, not p.owner == "") + "\n"

        return str_table

    __repr__ = __str__

    def __getitem__(self, idx):
        return self.table[idx]

    def __setitem__(self, idx, val):
        self.table[idx] = val

    def _insert_block(self, text: Union[List[str], str]) -> int:
        """
        Insert a new block into the block dictionary, and return its id.
        """
        lines = self.text_to_lines(text)
        index = max(self.blocks) + 1
        self.blocks[index] = lines
        return index

    def _insert_piece(self, piece: Piece, index: int = None,
                      after_id: str = None) -> None:
        """
        Inserts the given piece into the table, where either 'index' or
        'after_id' is specified.

        If 'index' is given, inserts the piece at this index into the table
        If 'after_id' is given, inserts the piece after the piece with this id
        into the table. If 'after_id' is an empty string, the piece is inserted
        as the first in the table.
        """
        if index is not None:
            self.table.insert(index, piece)
        elif after_id is not None:
            if after_id == "":
                index = 0
            else:
                index = self.get_piece_index(after_id) + 1
            self._insert_piece(piece, index=index)
        else:
            raise ValueError("No index or preceding uuid given")

    def _remove_piece(self, piece_id: str) -> None:
        """
        Remove the specified piece from the table.
        """
        piece = self.get_piece(piece_id)
        if piece:
            self.table.remove(piece)
        else:
            raise ValueError("Given uuid not in piece table")

    def _merge_neighbours_same_owner(self, piece_id: str, uname: str) -> None:
        """
        Merges the specified piece with its two neighbours if 'uname' owns
        the respective piece.

        Adds all block content to the block of the piece belonging to piece_id
        and removes the pieces which are now merged from the table.

        This function is called after a new lock has been put in the table, and
        thus assumes that the block_id belonging to piece_id is included as a
        whole in the table.
        """
        piece = self.get_piece(piece_id)
        index = self.get_piece_index(piece_id)

        # Try merging with the next piece in the table.
        if (index + 1 < len(self.table)
           and self.table[index + 1].owner == uname):
            next_piece = self.table[index + 1]
            next_block = self.get_lines(next_piece.piece_id, next_piece.start,
                                        next_piece.length)

            self.blocks[piece.block_id] += next_block
            piece.length += next_piece.length
            self.table.remove(next_piece)

        # Try merging with the previous piece in the table.
        if index > 0 and self.table[index - 1].owner == uname:
            prev_piece = self.table[index - 1]
            prev_block = self.get_lines(prev_piece.piece_id, prev_piece.start,
                                        prev_piece.length)

            self.blocks[piece.block_id] = (prev_block +
                                           self.blocks[piece.block_id])
            piece.length += prev_piece.length
            self.table.remove(prev_piece)

    def get_piece_index(self, piece_id: str) -> int:
        """
        From the given piece_id, return its index in the piece table. If it is
        not present, raises a ValueError.
        """
        for i, piece in enumerate(self.table):
            if piece.piece_id == piece_id:
                return i
        raise ValueError("Given uuid not in piece table")

    def get_piece(self, piece_id: str) -> Piece:
        """
        Return the piece given its id. If the piece is not present in the
        table, raises a ValueError.
        """
        for piece in self.table:
            if piece.piece_id == piece_id:
                return piece
        raise ValueError("Given uuid not in piece table")

    def row_to_piece(self, row: int) -> Tuple[str, int]:
        """
        Returns the piece_id which is located at the specified row in the file,
        as well as the offset within this piece.
        Raises a ValueError when the row is outside the file.
        """
        for piece in self.table:
            row -= piece.length
            if row <= 0:
                return piece.piece_id, piece.length + row
        raise ValueError("Row number out of bounds.")

    def piece_to_row(self, piece_id: str) -> int:
        """
        Returns the starting row of the specified piece, and raises a
        ValueError if the piece_id is not present in the table.
        """
        row = 0
        for piece in self.table:
            if piece.piece_id == piece_id:
                return row
            row += piece.length
        raise ValueError("Piece does not exist.")

    def get_pieces(self, start_piece_id: str, offset: int,
                   length: int) -> Tuple[List[Piece], int]:
        """
        Return a list of all pieces within the specified range. The range is
        given as the starting location, start_piece_id and offset, and the
        length of the range.

        Also returns 'end_offset', which indicates the last row in the last
        piece that is within the range.
        """
        start_index = self.get_piece_index(start_piece_id)
        pieces = []

        if (offset < 0 or offset >= self.table[start_index].length):
            raise ValueError("Offset is outside of starting piece.")

        # We want to compute the offset in the last block where the selection
        # ends. To do this, we compute the lines remaining in the last block,
        # and subtract it from the length of the last piece.
        remainder = -(length + offset)
        end_offset = 0

        for piece in self.table[start_index:]:
            pieces.append(piece)
            remainder += piece.length

            if remainder >= 0:
                break

        end_offset = piece.length - remainder

        return pieces, end_offset

    def get_piece_content(self, piece_id: str) -> List[str]:
        """
        Get the text content for a given piece id.
        """
        p = self.get_piece(piece_id)
        return self.blocks[p.block_id][p.start:p.start+p.length]

    def get_lines(self, start_piece_id: str = None, offset: int = 0,
                  length: int = None) -> List[str]:
        """
        Return actual text lines possibly spanning multiple pieces.

        If no start id is passed, starts from the first piece
        If length is not passed, returns the length until the end of the file.
        """
        if start_piece_id:
            start_index = self.get_piece_index(start_piece_id)
        else:
            start_index = 0

        if length is None:
            length = len(self)

        pieces = self.table[start_index:]
        first_piece, *rest_pieces = pieces

        length = min(sum(piece.length for piece in pieces) - offset, length)
        remaining_length = length

        # Step 1. Take the lines we need from the first piece
        start = first_piece.start + offset

        # We can never take more lines from the first piece than it contains,
        # so we need to take min(length, first_piece.length) lines.
        take_length = min(length, first_piece.length - offset)
        lines = self.blocks[first_piece.block_id][start:start + take_length]
        remaining_length -= take_length

        # Step 2. Take the remaining lines we need from the next pieces
        for piece in rest_pieces:
            if (remaining_length <= 0):
                break

            block = self.blocks[piece.block_id]
            take_length = min(remaining_length, piece.length)
            lines += block[piece.start:piece.start + take_length]
            remaining_length -= take_length

        assert remaining_length == 0
        assert len(lines) == length
        return lines

    def put_piece(self, start_piece_id: str, offset: int, length: int,
                  uname: str) -> str:
        """
        Locks a section of the piece table, meaning a new piece is put over
        one or more existing pieces, either partly or completely. Raises a
        ValueError when unsuccessful.

        Assigns 'uname' as the piece's owner.

        After calling this function, 'clear_unused_blocks' should be called
        to erase overwritten blocks from memory.
        """
        args = (start_piece_id, offset, length)

        # Get pieces and end offset
        pieces, end_offset = self.get_pieces(*args)

        # Check if allowed
        for p in pieces:
            if p.owner not in ("", uname):
                raise ValueError("The requested area is (partially) locked.")

        # Get lines and initiate new block
        lines = self.get_lines(*args)
        block_id = self._insert_block(lines)

        if len(pieces) > 1:
            (first_piece, *middle_pieces, last_piece) = pieces
        else:
            # This occurs when we're creating a piece fully inside another one.
            # In that case, we want to insert a copy of the piece after itself.
            first_piece = pieces[0]
            last_piece = Piece(*first_piece)
            self._insert_piece(last_piece, after_id=first_piece.piece_id)
            middle_pieces = []

        # Insert the new piece
        new_piece = Piece(piece_id=str(uuid.uuid4()), block_id=block_id,
                          start=0, length=len(lines), owner=uname)
        self._insert_piece(new_piece, after_id=first_piece.piece_id)

        # Cut starting piece
        if offset:
            first_piece.length = offset
            first_piece.piece_id = str(uuid.uuid4())
        else:
            self.table.remove(first_piece)

        # Remove pieces within range
        for piece in middle_pieces:
            self.table.remove(piece)

        # Cut last piece
        if not end_offset >= last_piece.length:
            last_piece.start += end_offset
            last_piece.length -= end_offset
            last_piece.piece_id = str(uuid.uuid4())
        else:
            self.table.remove(last_piece)

        # Merge the locks if necessary.
        self._merge_neighbours_same_owner(new_piece.piece_id, uname)

        return new_piece.piece_id

    def put_piece_after(self, piece_id: str, uname: str) -> str:
        """
        Inserts a new piece inbetween existing pieces after the piece
        with the given piece id.
        """
        block_id = self._insert_block("\n")
        piece = Piece(str(uuid.uuid4()), block_id, 0, 1, uname)
        self._insert_piece(piece, after_id=piece_id)
        self._merge_neighbours_same_owner(piece.piece_id, uname)
        return piece.piece_id

    def close_piece(self, piece_id: str) -> None:
        """
        After calling this function, 'merge_unlocked_pieces' could be called to
        potentially merge the piece with other unlocked pieces.
        """
        self.get_piece(piece_id).owner = ""

    def set_piece_content(self, piece_id: str, lines: List[str]) -> None:
        piece = self.get_piece(piece_id)
        if not piece.owner:
            raise LockError("Piece not locked.")
        assert piece.start == 0
        piece.length = len(lines)
        self.blocks[piece.block_id] = lines

    def merge_unlocked_pieces(self) -> None:
        """
        This function merges unlocked pieces by stitching the file and turning
        neighbouring unlocked pieces into a single piece referencing the new
        orig block (with id 0).

        After calling this function, 'clear_unused_blocks' should be called
        to erase the removed blocks from memory.
        """
        new_orig = self.get_lines()

        cur_pos = 0
        last_orig_index = 0
        for i, piece in enumerate(self.table):
            if piece.owner:
                # Skip locked blocks and update next 'orig' piece index.
                last_orig_index = i + 1
            else:
                if i == last_orig_index:
                    # Create new 'orig' piece.
                    piece.block_id = 0
                    piece.start = cur_pos
                else:
                    self.table[last_orig_index].length += piece.length
                    # Stage piece to be removed.
                    piece.piece_id = ""

            cur_pos += piece.length

        self.table = [piece for piece in self.table if piece.piece_id]
        self.blocks[0] = new_orig

    def clear_unused_blocks(self) -> List[int]:
        """
        Removes all unused blocks from the 'blocks' dictionary, and returns
        the block id's of the blocks which were removed from it.
        """
        used = {p.block_id for p in self.table} + {0}
        unused = {k for k in self.blocks if k not in used}

        self.blocks = {k: v for k, v in self.blocks.items() if k in used}

        return list(unused)
