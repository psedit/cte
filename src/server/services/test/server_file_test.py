import pytest
import sys
sys.path.insert(0, '.')
from server_file import ServerFile  # noqa
from cursor import Cursor  # noqa


@pytest.fixture(scope='class')
def sf():
    return ServerFile('./test', 'test_file.txt')


class TestSFDummy:
    def test_open_file(self, sf):
        assert hasattr(sf, 'pt')
        assert (sf.pt.get_lines() ==
                open('./test/test_file.txt', 'r').readlines())

    def test_client_join(self, sf):
        """
        When a client joins the file, its cursor should be put at the start
        of the first piece in the file's piece table.
        """
        sf.client_join('Sam')
        assert sf.cursors.get('Sam')
        cursor = sf.cursors['Sam']
        assert cursor.offset == 0
        assert cursor.column == 0
        assert cursor.piece_id == sf.pt[0].piece_id

    def test_add_lock(self, sf):
        sf.move_cursor('Sam', sf.pt[0].piece_id, 2, 10)
        sf.add_lock(sf.pt[0].piece_id, 2, 1, 'Sam')
        assert sf.cursors['Sam'] == Cursor(sf.pt[1].piece_id, 0, 10)
