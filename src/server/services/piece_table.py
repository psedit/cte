from typing import List, Tuple, Dict
import uuid
from piece import Piece
from typedefs import LockError


class PieceTable:
    """
    Text file data structure consisting of the original file together with
    so-called "edit-blocks" (see the TextBlock class), for which a table is
    used to couple these seperate blocks into one single file.

    Edit-blocks can can be created on top of the original file and locked, such
    that no other edit-blocks can be created on top of them, until the
    edit-block is closed manually. Edit-blocks can thereafter be edited such,
    while the piece table makes sure the general structure stays intact.
    """
    def __init__(self, text) -> None:
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
        fmt = "{:>38}" + "{:>10}"*5
        str_table = fmt.format("Piece ID", "Block ID", "Start",
                               "Length", "Owner", "Locked") + "\n"

        for p in self.table:
            str_table += fmt.format(*p, not p.owner == "") + "\n"

        return str_table

    def __getitem__(self, idx):
        return self.table[idx]

    def __setitem__(self, idx, val):
        self.table[idx] = val

    def _insert_block(self, text) -> int:
        """
        """
        lines = self.text_to_lines(text)
        index = max(self.blocks) + 1
        self.blocks[index] = lines
        return index

    def _remove_piece_block(self, p: Piece) -> None:
        if not p.length == len(self.blocks[p.block_id]):
            raise ValueError("Piece's block used by others")

        del self.blocks[p.block_id]

    def _insert_piece(self, piece: Piece, index: int = None,
                      after_id: str = None) -> None:
        """
        """
        if index is not None:
            self.table.insert(index, piece)
        elif after_id is not None:
            prev_index = self.get_piece_index(after_id) + 1
            self._insert_piece(piece, index=prev_index)
        else:
            raise ValueError("No index or preceding uuid given")

    def _clear_unused_blocks(self) -> None:
        used = [p.block_id for p in self.table]
        self.blocks = {k: v for k, v in self.blocks.items() if k in used}

    def _remove_piece(self, piece_id: str) -> None:
        piece = self.get_piece(piece_id)
        if piece:
            self.table.remove(piece)
        else:
            raise ValueError("Given uuid not in piece table")

    def _merge_neighbours_same_owner(self) -> None:
        cur_p = self.table[0]
        for next_p in self.table[1:]:
            if next_p.owner and next_p.owner == cur_p.owner:
                self.blocks[cur_p.block_id] += self.blocks[next_p.block_id]
                cur_p.length += next_p.length

                self._remove_piece_block(next_p)
                next_p.piece_id = ""
                cur_p.piece_id = str(uuid.uuid4())

                continue

            cur_p = next_p

        self.table = [p for p in self.table if p.piece_id]

    def get_piece_index(self, piece_id: str) -> int:
        """
        """
        for i, piece in enumerate(self.table):
            if piece.piece_id == piece_id:
                return i
        raise ValueError("Given uuid not in piece table")

    def get_piece(self, piece_id: str) -> Piece:
        """
        """
        for piece in self.table:
            if piece.piece_id == piece_id:
                return piece
        raise ValueError("Given uuid not in piece table")

    def row_to_piece(self, row: int) -> Tuple[str, int]:
        for piece in self.table:
            if row <= 0:
                return piece.piece_id, -row
            row -= piece.length
        raise ValueError("Row number out of bounds.")

    def piece_to_row(self, piece_id: str) -> int:
        row = 0
        for piece in self.table:
            if piece.piece_id == piece_id:
                return row
            row += piece.length
        return -1

    def get_pieces(self, start_piece_id: str, offset: int,
                   length: int) -> Tuple[List[Piece], int]:
        """
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
        """ Get the content for a given piece id. """
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
            # In that case, we want to insert a copy of the piece after itself,
            # and insert
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

        # Clean unused blocks
        # (maybe breaks things client-side, so removing it)
        # self._clear_unused_blocks()
        return new_piece.piece_id

    def close_piece(self, piece_id: str) -> None:
        self.get_piece(piece_id).owner = ""

    def set_piece_content(self, piece_id: str, lines: List[str]) -> None:
        piece = self.get_piece(piece_id)
        if not piece.owner:
            raise LockError("Piece not locked.")
        assert piece.start == 0
        piece.length = len(lines)
        self.blocks[piece.block_id] = lines

    def merge_unlocked_pieces(self):
        """
        This function merges unlocked pieces by stitching the file and turning
        contiguous unlocked blocks into a single block with the s
        """
        new_orig = self.get_lines()

        cur_pos = 0
        last_orig_index = 0
        for i, piece in enumerate(self.table):
            if piece.owner:
                # Skip locked blocks and update next 'orig' piece index.
                last_orig_index = i + 1
            else:
                self.table[last_orig_index].length += piece.length

                if i == last_orig_index:
                    # Create new 'orig' piece.
                    piece.block_id = 0
                    piece.start = cur_pos
                else:
                    # Stage piece to be removed.
                    piece.piece_id = ""

            cur_pos += piece.length

        self.table = [piece for piece in self.table if piece.piece_id]
        self.blocks[0] = new_orig
        self._clear_unused_blocks()
