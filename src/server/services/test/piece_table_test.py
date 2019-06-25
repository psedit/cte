import sys
import pdb
sys.path.insert(0, '.')
from piece_table import PieceTable
import pytest

test_text = "test0\ntekst1\ntest2\ntekst3\ntest4\ntekst5\ntest6\ntekst7"


@pytest.fixture
def piece_table():
    return PieceTable(test_text)


def test_contains_original(piece_table):
    assert len(piece_table.blocks) == 1
    assert piece_table.blocks[0]
    assert piece_table[0] == piece_table.table[0]


def test_table_splits_text(piece_table):
    block_id = piece_table.table[0].block_id
    assert piece_table.blocks[block_id] == test_text.splitlines(True)
    assert len(piece_table) == len(test_text.splitlines(True))


def test_insert_block(piece_table):
    insert_text = ["kaas", "kaas", "kaas"]
    piece_table._insert_block(insert_text)
    assert piece_table.blocks[1] == insert_text


def test_first_piece_get_lines(piece_table):
    substr = piece_table.get_lines(0, 2, 3)
    assert substr == "test2\ntekst3\ntest4\n".splitlines(True)


def test_single_piece_pt_length(piece_table):
    assert len(piece_table) == len(test_text.split('\n'))


def test_clear_unused_blocks(piece_table):
    pass


def test_put_piece(piece_table):
    table = piece_table.table
    prev_orig_id = table[0].piece_id
    piece_table.put_piece(prev_orig_id, 2, 3, "tester")

    assert piece_table.blocks[1] == "test2\ntekst3\ntest4\n".splitlines(True)
    assert piece_table.get_lines() == test_text.splitlines(True)

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


def test_put_multiple_pieces(piece_table):
    table = piece_table.table
    prev_orig_id = table[0].piece_id

    piece_table.put_piece(prev_orig_id, 1, 1, "tester")
    piece1_id = table[-1].piece_id
    piece_table.put_piece(piece1_id, 1, 2, "tester")
    piece2_id = table[-1].piece_id
    piece_table.put_piece(piece2_id, 1, 1, "tester")

    assert len(table) == 7
    assert piece_table.get_lines() == test_text.splitlines(True)


def test_put_piece_full(piece_table):
    table = piece_table.table
    prev_orig_id = table[0].piece_id

    piece_table.put_piece(prev_orig_id, 0, 8, "tester")

    assert len(table) == 1
    assert piece_table.get_lines() == test_text.splitlines(True)


def test_put_piece_edges(piece_table):
    table = piece_table.table
    prev_orig_id = table[0].piece_id

    piece_table.put_piece(prev_orig_id, 0, 4, "tester")
    piece1_id = table[-1].piece_id
    piece_table.put_piece(piece1_id, 0, 4, "tester2")

    assert len(table) == 2
    assert piece_table.get_lines() == test_text.splitlines(True)

def test_put_piece_outside(piece_table):
    table = piece_table.table
    prev_orig_id = table[0].piece_id

    with pytest.raises(ValueError):
        piece_table.put_piece(prev_orig_id, -2, 4, "tester")
    with pytest.raises(ValueError):
        piece_table.put_piece(prev_orig_id, 9, 4, "tester")

    piece_table.put_piece(prev_orig_id, 2, 10, "tester")
    assert len(table) == 2
    assert piece_table.get_lines() == test_text.splitlines(True)


def test_close_and_partly_overwrite_piece(piece_table):
    table = piece_table.table
    prev_orig_id = table[0].piece_id
    piece_table.put_piece(prev_orig_id, 2, 3, "tester1")

    piece_id = table[1].piece_id
    piece_table.close_piece(piece_id)

    piece_table.put_piece(piece_id, 2, 2, "tester2")

    assert piece_table.get_lines() == test_text.splitlines(True)
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


def test_put_piece_on_closed_piece(piece_table):
    table = piece_table.table
    prev_orig_id = table[0].piece_id
    piece_table.put_piece(prev_orig_id, 2, 3, "tester1")
    piece_id = table[1].piece_id

    with pytest.raises(ValueError):
        piece_table.put_piece(prev_orig_id, 1, 5, "tester2")
    with pytest.raises(ValueError):
        piece_table.put_piece(piece_id, 1, 4, "tester2")
    with pytest.raises(ValueError):
        piece_table.put_piece(piece_id, 0, 3, "tester2")


def test_remove_unused_pieces(piece_table):
    table = piece_table.table
    prev_orig_id = table[0].piece_id

    piece_table.put_piece(prev_orig_id, 2, 2, "tester")
    piece_table.put_piece(table[-1].piece_id, 0, 2, "tester2")

    piece_table.close_piece(table[1].piece_id)
    piece_table.close_piece(table[2].piece_id)

    piece_table.put_piece(table[0].piece_id, 1, 5, "tester")

    assert [1,2] == piece_table.clear_unused_blocks()

    assert len(table) == 3
    assert table[0].length == 1
    assert table[1].length == 5
    assert table[2].length == 2
    assert piece_table.get_lines() == test_text.splitlines(True)

    block_text = "tekst1\ntest2\ntekst3\ntest4\ntekst5\n"
    assert len(piece_table.blocks) == 2
    assert piece_table.blocks[3] == block_text.splitlines(True)
    with pytest.raises(KeyError):
        piece_table.blocks[1]
        piece_table.blocks[2]


def test_set_piece_content(piece_table):
    table = piece_table.table
    prev_orig_id = table[0].piece_id

    piece_table.put_piece(prev_orig_id, 2, 2, "tester")

    piece_table.set_piece_content(table[1].piece_id, ["kaas\n"]*10)

    new_text = "test0\ntekst1\n" + "kaas\n"*10 + "test4\ntekst5\ntest6\ntekst7"
    assert len(piece_table.get_lines()) == 16
    assert piece_table.get_lines() == new_text.splitlines(True)


def test_get_whole_file(piece_table):
    assert piece_table.get_lines() == test_text.splitlines(True)
