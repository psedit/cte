from typing import List, Tuple, Dict, Any
from text_block import TextBlock
import uuid

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
        if isinstance(text, str):
            lines = text.splitlines(True)
        else:
            lines = text

        orig_piece = TextBlock(lines, False)
        orig_piece_id = str(uuid.uuid4())
        print("###########################")
        print(orig_piece_id)
        print("###########################")
        self.blocks: Dict[int, TextBlock] = {0: orig_piece}
        self.table: List[List[Any]] = [[orig_piece_id, 0, 0, len(lines)]]

    def __len__(self) -> int:
        """
        Returns the length of the stitched file according to the piece table.
        """
        return sum(entry[3] for entry in self.table)

    def __str__(self) -> str:
        fmt = "{:>38}" + "{:>10}"*4
        str_table = fmt.format("Piece ID", "Block ID", "Start", "Length", "Open") + "\n"

        for p in self.table:
            str_table += fmt.format(*p, self.blocks[p[0]].is_open()) + "\n"

        return str_table

    def line_to_table_index(self, line: int) -> Tuple[int, int]:
        """
        Returns the corresponding piece index and piece offset
        for a given file line.
        """
        piece_start: int = 0
        for i, entry in enumerate(self.table):
            piece_length: int = entry[3]

            if line >= piece_start and line < piece_start + piece_length:
                return i, line - piece_start

            piece_start += piece_length
        raise ValueError("Invalid line number")

    def get_piece_start(self, piece_id: str) -> int:
        """
        Returns the line at which the given piece (table index) begins within
        the stitched file. Return -1 when the piece is not in the table.
        """
        cur_loc: int = 0
        for piece in self.table:
            if piece[0] == piece_id:
                return cur_loc
            cur_loc += piece[3]
        return -1

    def get_piece_range(self, start: int, length: int) -> Tuple[int, int]:
        """
        Returns a range of pieces which cover the given line range, in the
        form '(start_pieces, end_piece)'.
        """
        first, offset = self.line_to_table_index(start)
        length_rem: int = length - (self.table[first][3] - offset)
        last_off: int = 1

        while length_rem > 0 and first + last_off < len(self.table):
            length_rem -= self.table[first + last_off][3]
            last_off += 1

        return first, first + last_off - 1

    def get_lines(self, start: int, length: int) -> List[str]:
        """
        Returns a list with the requested lines assembled
        from the piece present in the piece table.

        When length is -1, returns until the last line.
        """
        if length < 0:
            length = len(self)

        lines: List[str] = []
        length_rem: int = length
        index, offset = self.line_to_table_index(start)
        first, last = self.get_piece_range(start, length)

        for i in range(first, last + 1):
            piece_id, block_id, line_s, line_c = self.table[i]
            block = self.blocks[block_id]

            if i == first:
                line_s += offset
                line_c -= offset

            lines.extend(block.get_lines(line_s, min(length_rem, line_c)))

            length_rem -= line_c

        return lines

    def get_piece_info(self, piece_id: str) -> List[int]:
        """
        If the given block is locked, returns the current piece length
        and starting location within the file.
        """
        # TODO
        cur_pos = 0
        for piece in self.table:
            if piece[0] == piece_id:
                return [cur_pos, piece[3]]
            else:
                cur_pos += piece[3]
        return []

    def get_piece_content(self, piece_id: str) -> List[str]:
        """
        Returns the content of a single piece in the table.
        """
        for p_id, block_id, start, length in self.table:
            if p_id == piece_id:
                return self.blocks[block_id].get_lines(start, length)

        return []

    def get_piece_block_id(self, piece_id: str) -> int:
        """
        Returns the block id of a single piece in the table.
        """
        for p_id, block_id, _, _ in self.table:
            if p_id == piece_id:
                return block_id

        return -1

    def stitch(self) -> List[str]:
        """
        Returns the new stitched file according to the piece table.
        """
        stitched_file: List[str] = []
        position = 0
        for _, block_id, start, length in self.table:
            position += length

            stitched_file.extend(self.blocks[block_id].get_lines(start, length))

        return stitched_file

    def remove_closed_blocks(self) -> List[str]:
        """
        Stitches the file and removes closed edit-blocks. The new generated
        pieces are given a new uuid, while the locked blocks retain their
        original ID such that their user remains known for the clients.

        Use when saving to disk.
        """
        stitched_file = self.stitch()
        self.blocks[0] = TextBlock(stitched_file)

        # Update the table section lengths and starting positions
        cur_pos = 0
        last_open_index = 0
        for i, section in enumerate(self.table):
            if self.blocks[section[1]].is_open():
                last_open_index = i + 1
            else:
                self.table[last_open_index][3] += section[3]

                if i is last_open_index:
                    # Move the section to 'orig' and give it a new uuid.
                    section = [str(uuid.uuid4()), 0, cur_pos, section[3]]
                else:
                    # The empty uuid signals that the section is to be removed.
                    section[0] = ""

            cur_pos += section[2]

            # Generate new uuid's
            section[0] = str(uuid.uuid4())

        self.table = [s for s in self.table if not s[0] is ""]

        # Remove the closed blocks from memory
        for block_id in self.blocks:
            if not self.blocks[block_id].is_open():
                del self.blocks[block_id]

        return stitched_file

    def open_block(self, piece_id: str, offset: int, length: int) -> str:
        """
        Opens a new block in the piece table starting at the given offset
        within the specified piece, until the given length.

        Raises a ValueError when trying to open a locked area, or when outside
        of file boundaries.

        Returns the piece uuid of the created block when successful, and an
        exception describing the occurred error otherwise. Also updates the
        uuid's of all affected blocks.
        """
        # Get the starting position of the piece
        piece_start = self.get_piece_start(piece_id)

        if piece_start < 0:
            # The piece uuid is not present in the piece table.
            raise ValueError("Piece uuid is not present within the table.")

        start = piece_start + offset

        # Check if block creation is allowed
        range_start, range_end = self.get_piece_range(start, length)
        for piece in self.table[range_start:range_end + 1]:
            if self.blocks[piece[1]].is_open():
                raise ValueError("Illegal block request, the area is locked.")

        if start + length > len(self):
            raise ValueError("Illegal block request, end of file.")

        # Create the new TextBlock object
        block_lines: List[str] = self.get_lines(start, length)

        new_block: TextBlock = TextBlock(block_lines)
        block_id = max(self.blocks) + 1
        self.blocks[block_id] = new_block

        # Find and shrink previous containing block.
        index, offset = self.line_to_table_index(start)
        prev_len: int = self.table[index][2]
        self.table[index][0] = str(uuid.uuid4())
        self.table[index][2] = offset

        # Insert the new block in the table
        piece_id = str(uuid.uuid4())
        self.table.insert(index + 1, [piece_id,
                                      len(self.blocks) - 1,
                                      0, length])

        # Update the rest of the table
        rem: int = prev_len - (offset + length)
        if rem > 0:
            # Insert remainder of previous containing block after new block
            n_start = self.table[index][2] + offset + length

            self.table.insert(index + 2, [str(uuid.uuid4()),
                                          self.table[index][1],
                                          n_start, rem])
        else:
            # Cut or shrink the next couple blocks to make space
            length_rem: int = -1 * rem
            cur_piece_index: int = index + 2

            while length_rem > 0 and len(self.table) > cur_piece_index:
                piece_len: int = self.table[cur_piece_index][3]

                if length_rem > piece_len:
                    length_rem -= piece_len
                    del self.table[cur_piece_index]
                else:
                    self.table[cur_piece_index][0] = str(uuid.uuid4())
                    self.table[cur_piece_index][2] += length_rem
                    self.table[cur_piece_index][3] -= length_rem

                    break

        return piece_id

    def close_block(self, piece_id: str) -> None:
        """
        Closes the block with the corresponsing index.

        The block is kept within the piece table but should not be written to
        anymore.
        """
        for piece in self.table:
            if piece[0] == piece_id:
                self.blocks[piece[1]].close()
