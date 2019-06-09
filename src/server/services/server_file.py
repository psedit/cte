from typing import List, Tuple
from client import Address

Range = Tuple[int, int]


class ServerFile:
    def __init__(self, root: str, path: str) -> None:
        self.root_dir: str = root
        self.file_path_relative: str = path

        self.load_file()

    def load_file(self) -> None:
        """Create the mmap file object (Loads the file into virtual memory).
        """
        # f = os.open(os.path.join(self.root_dir, self.file_path_relative),
        #             os.O_RDWR)
        pass

    def retrieve_block(self, start: int = 0, end: int = -1) -> List[str]:
        """Returns all line between (and including) a start and end line, split
        up per line.

        Keyword arguments:
        start -- Line number indicating start position
        end -- Line number indicating end position, -1 indicates the last line.
        """
        if self.file_mmap:
            self.file_mmap.seek(0)
            block: List[str] = []

            for i, line in enumerate(iter(self.file_mmap.readline, b"")):
                if start <= i and (end < 0 or i <= end):
                    block.append(line.decode('utf-8'))

            return block
        else:
            pass

    def save_buffer(self) -> None:
        """Writes the current buffer to the file on disk, although the mmap
        automatically writes to disk in most instances.
        """
        self.file_mmap.flush()

    def update_buffer(self, delta) -> None:
        """ Writes the the delta contents (= file change) to the buffer.
        """
        # TODO: Keep locks in mind
        # TODO: Return error code(?)
        pass

    def add_lock(self, delta) -> int:
        # TODO: Return error code(?)
        pass

    def remove_lock(self, delta) -> None:
        # TODO: Return error code(?)
        pass

    def move_cursor(self, client: Address, row: int, column: int) -> None:
        self.file_buffer.move_cursor(client, row, column)

    def get_cursor(self, client) -> Tuple[int, int]:
        return self.file_buffer.get_cursor_list()

    def drop_cursor(self, client) -> None:
        self.file_buffer.remove_cursor(client)
