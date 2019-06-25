import dataclasses


@dataclasses.dataclass
class Cursor:
    piece_id: str
    offset: int
    column: int

    def _get_fields(self):
        return [getattr(self, field) for field in self.__annotations__]

    def __iter__(self):
        for field in self._get_fields():
            yield field