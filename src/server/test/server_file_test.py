import pytest
from services.server_file import ServerFile
from services.cursor import Cursor
from services.typedefs import LockError


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
        assert sf.is_joined("Sam") is True

    def test_add_lock(self, sf):
        sf.move_cursor('Sam', sf.pt[0].piece_id, 2, 10)
        sf.add_lock(sf.pt[0].piece_id, 2, 1, 'Sam')
        assert sf.cursors['Sam'] == Cursor(sf.pt[1].piece_id, 0, 10)

    def test_cursor(self, sf):
        uuid, offset, column = sf.cursors['Sam']
        assert uuid == sf.cursors['Sam'].piece_id
        assert offset == sf.cursors['Sam'].offset
        assert column == sf.cursors['Sam'].column
        cursor_list = sf.get_cursor_list()
        assert cursor_list == {"Sam": Cursor(sf.pt[1].piece_id, 0, 10)}

    def test_illegal_lock(self, sf):
        sf.client_join("Robin")
        with pytest.raises(LockError):
            sf.add_lock(sf.pt[1].piece_id, 0, 1, "Robin")

    def test_insert_lock_after_piece(self, sf):
        piece_id = sf.insert_lock_after_piece(sf.pt[1].piece_id, "Robin")
        assert len(sf.pt.table) == 4
        assert sf.pt[2].piece_id == piece_id
        assert sf.pt[2].owner == "Robin"
        assert len(sf.pt) == 5

    def test_change_lock_owner(self, sf):
        sf.change_lock_owner(sf.pt[1].piece_id, "Robin")
        assert sf.pt[1].owner == "Robin"

    def test_remove_lock(self, sf):
        sf.remove_lock(sf.pt[2].piece_id)
        sf.remove_lock(sf.pt[1].piece_id)
        assert len(sf.pt.table) == 1
        assert sf.pt[0].owner == ""

    def test_illegal_cursor_move(self, sf):
        res = sf.move_cursor("Robin", "kaas", 10, 2)
        assert res is None

    def test_get_clients(self, sf):
        assert sf.get_clients() == ["Sam", "Robin"]

    def test_client_count(self, sf):
        assert sf.client_count() == 2

    def test_file_save(self, sf):
        sf.save_to_disk()
        assert (open('./test/test_file.txt', 'r').readlines() ==
                sf.pt.get_lines())

    def test_update_content(self, sf):
        lock_id = sf.add_lock(sf.pt[0].piece_id, 0, 2, "Sam")
        sf.update_content("Sam", lock_id, "Plakje kaas")
        assert sf.pt.get_piece_content(lock_id) == ["Plakje kaas"]

    def test_change_file_path(self, sf):
        sf.change_file_path("./kaas.txt")
        assert sf.path_relative == "./kaas.txt"

    def test_client_leave(self, sf):
        sf.client_leave("Sam")
        assert "Sam" not in sf.get_clients()
        assert all(p.owner != "Sam" for p in sf.pt.table)
