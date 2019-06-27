The CTE infrastructure needs to keep track of file content dynamically such that clients can update parts of a file, so called blocks.

# Piece Table
A file is chopped up into smaller blocks, the so called pieces.
Each piece has a unique identifier, a block identifier, the starting line number (0-based), the number of lines and whether it has been opened (true/false).

E.g. kaas_is_dood.txt contains the line `rip` which will be sent as:
```
{'piece_table': [['18b74691-85f2-4d97-a488-79a367b502aa', 0, 0, 1]], 'block_list': [[0, False, ['rip']]]}
```
with piece table:
```
'piece_table': [['18b74691-85f2-4d97-a488-79a367b502aa', 0, 0, 1]]
```
and raw block list:
```
'block_list': [[0, False, ['rip']]]
```

# Block List
TBD