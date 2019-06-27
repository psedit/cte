import pytest
from services.piece_table import PieceTable
from services.piece import Piece
from services.typedefs import LockError

test_text = "test0\ntekst1\ntest2\ntekst3\ntest4\ntekst5\ntest6\ntekst7"


@pytest.fixture
def pt():
    return PieceTable(test_text)


def test_create_empty_file(pt):
    pt_2 = PieceTable("")
    table = pt_2.table

    assert len(table) == 1
    assert table[0].length == 1
    assert pt_2.blocks[table[0].block_id] == ["\n"]


def test_contains_original(pt):
    assert len(pt.blocks) == 1
    assert pt.blocks[0]
    assert pt[0] == pt.table[0]


def test_table_splits_text(pt):
    block_id = pt.table[0].block_id
    assert pt.blocks[block_id] == test_text.splitlines(True)
    assert len(pt) == len(test_text.splitlines(True))


def test_insert_block(pt):
    insert_text = ["kaas", "kaas", "kaas"]
    pt._insert_block(insert_text)
    assert pt.blocks[1] == insert_text


def test_first_piece_get_lines(pt):
    substr = pt.get_lines(0, 2, 3)
    assert substr == "test2\ntekst3\ntest4\n".splitlines(True)
    assert pt.get_lines() == test_text.splitlines(True)


def test_single_piece_pt_length(pt):
    assert len(pt) == len(test_text.split('\n'))


def test_row_to_piece_and_back(pt):
    with pytest.raises(ValueError):
        pt.row_to_piece(1000)
    with pytest.raises(ValueError):
        pt.piece_to_row("not_existing_id")


def test_insert_piece_in_table(pt):
    text = test_text.splitlines(True)
    piece = Piece("test_id", 0, 2, 4, "")
    first_uuid = pt[0].piece_id
    pt._insert_piece(piece, after_id=first_uuid)

    assert len(pt.table) == 2
    assert pt[1].piece_id == "test_id"
    assert pt.get_lines() == text + text[2:6]

    pt._insert_piece(piece, after_id="")

    assert len(pt.table) == 3
    assert pt[0].piece_id == "test_id"
    assert pt[1].piece_id == first_uuid
    assert pt[2].piece_id == "test_id"
    assert pt.get_lines() == text[2:6] + text + text[2:6]

    piece_2 = Piece("test_id_2", 0, 0, 2, "")

    pt._insert_piece(piece_2, index=2)

    assert len(pt.table) == 4
    assert pt[2].piece_id == "test_id_2"

    with pytest.raises(ValueError):
        pt._insert_piece(piece_2)


def test_remove_piece(pt):
    pt._insert_piece(Piece("test_id", 0, 2, 4, ""), index=0)

    pt._remove_piece("test_id")

    assert len(pt.table) == 1
    assert pt.get_lines() == test_text.splitlines(True)

    with pytest.raises(ValueError):
        pt._remove_piece("id_not_in_table")


def test_put_piece(pt):
    table = pt.table
    prev_orig_id = table[0].piece_id
    pt.put_piece(prev_orig_id, 2, 3, "tester")

    assert pt.blocks[1] == "test2\ntekst3\ntest4\n".splitlines(True)
    assert pt.get_lines() == test_text.splitlines(True)

    assert len(table) == 3
    assert table[0].block_id == 0
    assert table[1].block_id == 1
    assert table[2].block_id == 0

    assert table[0].start == 0
    assert table[0].length == 2
    assert table[1].start == 0
    assert table[1].length == 3
    assert table[2].start == 5
    assert table[2].length == 3

    assert len({prev_orig_id, table[0].piece_id, table[1].piece_id,
                table[2].piece_id}) == 4


def test_put_multiple_pieces(pt):
    table = pt.table
    prev_orig_id = table[0].piece_id

    pt.put_piece(prev_orig_id, 1, 1, "tester")
    piece1_id = table[-1].piece_id
    pt.put_piece(piece1_id, 1, 2, "tester")
    piece2_id = table[-1].piece_id
    pt.put_piece(piece2_id, 1, 1, "tester")

    assert len(table) == 7
    assert pt.get_lines() == test_text.splitlines(True)


def test_put_piece_full(pt):
    table = pt.table
    prev_orig_id = table[0].piece_id

    pt.put_piece(prev_orig_id, 0, 8, "tester")

    assert len(table) == 1
    assert pt.blocks[0] == test_text.splitlines(True)
    assert pt.get_lines() == test_text.splitlines(True)


def test_put_piece_edges(pt):
    table = pt.table
    prev_orig_id = table[0].piece_id

    pt.put_piece(prev_orig_id, 0, 4, "tester")
    piece1_id = table[-1].piece_id
    pt.put_piece(piece1_id, 0, 4, "tester2")

    assert len(table) == 2
    assert pt.get_lines() == test_text.splitlines(True)


def test_put_piece_outside(pt):
    table = pt.table
    prev_orig_id = table[0].piece_id

    with pytest.raises(ValueError):
        pt.put_piece(prev_orig_id, -2, 4, "tester")
    with pytest.raises(ValueError):
        pt.put_piece(prev_orig_id, 9, 4, "tester")

    pt.put_piece(prev_orig_id, 2, 10, "tester")
    assert len(table) == 2
    assert pt.get_lines() == test_text.splitlines(True)


def test_merge_adjacent_locked_pieces(pt):
    table = pt.table
    text = test_text.splitlines(True)
    pt.put_piece(table[-1].piece_id, 1, 1, "tester")
    pt.put_piece(table[-1].piece_id, 0, 2, "tester")

    assert len(table) == 3
    assert table[0].owner == ""
    assert table[1].owner == "tester"
    assert table[2].owner == ""

    assert table[1].length == 3
    assert pt.blocks[table[1].block_id] == text[1:4]

    pt.put_piece(pt[0].piece_id, 0, 1, "tester")

    assert len(table) == 2
    assert table[0].owner == "tester"
    assert table[1].owner == ""

    assert pt.get_lines() == test_text.splitlines(True)

    pt.put_piece(pt[-1].piece_id, 1, 1, "tester")
    assert len(table) == 4
    pt.put_piece(pt[-3].piece_id, 0, 1, "tester")

    assert len(table) == 2
    assert table[0].owner == "tester"
    assert table[1].owner == ""
    assert pt.get_lines() == test_text.splitlines(True)


def test_close_and_partly_overwrite_piece(pt):
    table = pt.table
    prev_orig_id = table[0].piece_id
    pt.put_piece(prev_orig_id, 2, 3, "tester1")

    piece_id = table[1].piece_id
    pt.close_piece(piece_id)

    pt.put_piece(piece_id, 2, 2, "tester2")

    assert pt.get_lines() == test_text.splitlines(True)
    assert table[0].block_id == 0
    assert table[1].block_id == 1
    assert table[2].block_id == 2
    assert table[3].block_id == 0

    assert table[0].start == 0
    assert table[0].length == 2
    assert table[1].start == 0
    assert table[1].length == 2
    assert table[2].start == 0
    assert table[2].length == 2
    assert table[3].start == 6
    assert table[3].length == 2


def test_put_piece_on_closed_piece(pt):
    table = pt.table
    prev_orig_id = table[0].piece_id
    pt.put_piece(prev_orig_id, 2, 3, "tester1")
    piece_id = table[1].piece_id

    with pytest.raises(ValueError):
        pt.put_piece(prev_orig_id, 1, 5, "tester2")
    with pytest.raises(ValueError):
        pt.put_piece(piece_id, 1, 4, "tester2")
    with pytest.raises(ValueError):
        pt.put_piece(piece_id, 0, 3, "tester2")


def test_remove_unused_pieces(pt):
    table = pt.table
    prev_orig_id = table[0].piece_id

    pt.put_piece(prev_orig_id, 2, 2, "tester")
    pt.put_piece(table[-1].piece_id, 0, 2, "tester2")

    pt.close_piece(table[1].piece_id)
    pt.close_piece(table[2].piece_id)

    pt.put_piece(table[0].piece_id, 1, 5, "tester")

    assert [1, 2] == pt.clear_unused_blocks()

    assert len(table) == 3
    assert table[0].length == 1
    assert table[1].length == 5
    assert table[2].length == 2
    assert pt.get_lines() == test_text.splitlines(True)

    block_text = "tekst1\ntest2\ntekst3\ntest4\ntekst5\n"
    assert len(pt.blocks) == 2
    assert pt.blocks[3] == block_text.splitlines(True)
    with pytest.raises(KeyError):
        pt.blocks[1]
    with pytest.raises(KeyError):
        pt.blocks[2]


def test_set_piece_content(pt):
    table = pt.table
    prev_orig_id = table[0].piece_id

    pt.put_piece(prev_orig_id, 2, 2, "tester")

    pt.set_piece_content(table[1].piece_id, ["kaas\n"]*10)

    new_text = "test0\ntekst1\n" + "kaas\n"*10 + "test4\ntekst5\ntest6\ntekst7"
    assert len(pt.get_lines()) == 16
    assert pt.get_lines() == new_text.splitlines(True)


def test_get_whole_file(pt):
    assert pt.get_lines() == test_text.splitlines(True)


def test_stringify_pt(pt):
    pt.put_piece(pt[0].piece_id, 2, 3, "Gerard")
    pt_str = str(pt)
    assert 'Gerard' in pt_str


def test_merge_unlocked(pt):
    pt.put_piece(pt[0].piece_id, 2, 3, "Gerard")
    assert len(pt.table) == 3
    # Unlock
    pt[1].owner = ""
    pt.merge_unlocked_pieces()
    assert len(pt.table) == 1


def test_set_unlocked_content(pt):
    with pytest.raises(LockError):
        pt.set_piece_content(pt[0].piece_id, ["foo\n", "bar\n"])


def test_get_piece_content(pt):
    assert pt.get_piece_content(pt[0].piece_id) == test_text.splitlines(True)
    lock_id = pt.put_piece(pt[0].piece_id, 2, 1, "Gerard")
    assert pt.get_piece_content(lock_id) == ["test2\n"]
