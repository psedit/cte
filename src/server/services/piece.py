import dataclasses


@dataclasses.dataclass
class Piece:
    piece_id: str
    block_id: int
    start:    int
    length:   int
    owner:    str

    def _get_fields(self):
        return [getattr(self, field) for field in self.__annotations__]

    def __iter__(self):
        for field in self._get_fields():
            yield field
