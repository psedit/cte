import mmap
from typing import List
import os


class ServerFile:
    root_dir: str
    file_path_relative: str
    file_mmap: mmap

    def __init__(self, root: str, path: str) -> None:
        self.root_dir = root
        self.file_path_relative = path

        self.load_file()

    def load_file(self) -> None:
        """Create the mmap file object (Loads the file into virtual memory).
        """

        f = os.open(self.root_dir + self.file_path_relative, os.O_RDWR)
        self.file_mmap = mmap.mmap(f,0,prot=mmap.PROT_READ | mmap.PROT_WRITE)

    def retrieve_block(self, start: int = 0, end: int = -1) -> List[str]:
        """Returns all line between (and including) a start and end line, split
        up per line.

        Keyword arguments:
        start -- Line number indicating start position
        end -- Line number indicating end position, -1 indicates the last line.
        """

        if self.file_mmap is not None:
            self.file_mmap.seek(0)
            block: List[str] = []

            for i, line in enumerate(iter(self.file_mmap.readline, b"")):
                if start <= i and (end < 0 or i <= end):
                    block.append(line)

            return block
        else:
            pass
