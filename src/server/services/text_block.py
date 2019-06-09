from typing import List


class TextBlock:
    """
    Text blocks for use in the PieceTable class. Will mainly be locked and
    previously locked edit-blocks created by clients.
    """
    def __init__(self, lines, is_open: bool = True) -> None:
        self.is_open: bool = is_open
        self.lines: List[str] = lines

    def __len__(self) -> int:
        return len(self.lines)
        
    def update(self, delta) -> None:
        # TODO
        pass
    
    def get_lines(self, start: int, length: int) -> List[str]:
        return self.lines[start:start + length]
    
    def close(self) -> None:
        self.is_open = False
        
    def status(self) -> bool:
        return self.is_open