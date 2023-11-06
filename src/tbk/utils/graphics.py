"""Text-based display of normally more graphical elements."""
from collections.abc import Iterable, Sequence
from typing import Any, Literal, Union

def _str_table(
    table: list[list[list[str]]],
    col_alignments: Sequence[int],
    row_alignments: Sequence[int],
) -> str:
    """See documentation for str_table().
    Exception: table is a table of lists of lines instead of strs.
    """
    max_widths = [max(len(line) for row in range(len(table))
                      for line in table[row][col])
                  for col in range(len(table[0]))]
    max_heights = [max(len(cell) for cell in row)
                   for row in table]

    # pad table IN PLACE
    for row, max_height, row_alignment in zip(table, max_heights, row_alignments):
        for cell, max_width, col_alignment in zip(row, max_widths, col_alignments):
            # vertically pad with newlines IN PLACE
            num_lines = len(cell)
            match row_alignment:
                case -1: # top
                    # append empty lines
                    cell.extend([''] * (max_height - num_lines))
                case 0: # middle
                    count, odd = divmod(max_height - num_lines, 2)
                    cell[:] = [''] * (count + odd) + cell + [''] * count
                case 1: # bottom
                    # prepend empty lines
                    cell[:0] = [''] * (max_height - num_lines)
                case x:
                    raise ValueError(f'invalid alignment {x!r}')
            # horizontally pad with spaces IN PLACE
            method = {-1: str.ljust, 0: str.center, 1: str.rjust}[col_alignment]
            cell[:] = [method(line, max_width) for line in cell]
    col_sep = '|'
    row_sep = '+'.join('-' * (max_width + 2) # include surrounding spaces
                       for max_width in max_widths)
    row_sep = f'\n{row_sep}\n'
    return row_sep.join(
        '\n'.join(
            col_sep.join(f' {cell[i]} ' for cell in row)
            for i in range(max_height)
        ) for row, max_height in zip(table, max_heights)
    )

def str_table(
    table: Iterable[Iterable[Any]],
    col_alignments: Union[
        Iterable[Literal[-1, 0, 1]],
        Literal[-1, 0, 1]
    ] = -1,
    row_alignments: Union[
        Iterable[Literal[-1, 0, 1]],
        Literal[-1, 0, 1]
    ] = 0,
) -> str:
    """Convert a row-major table of values to a text table of their str()s.

    Args:
        table: Iterable of rows (iterables) of str()-able objects.
            Each row must be of the same length.
        col_alignments: Iterable of -1 (left) / 0 (center) / 1 (right)
            column alignments; or a single such value to apply to all columns.
        row_alignments: Iterable of -1 (top) / 0 (middle) / 1 (bottom)
            row alignments; or a single such value to apply to all rows.

    Returns:
        ASCII table of the values, suitable for printing.
    """
    strs_table = [[str(cell).splitlines() for cell in row] for row in table]
    if isinstance(col_alignments, Iterable):
        cols = list(col_alignments)
    else:
        cols = [col_alignments] * len(strs_table[0])
    if isinstance(row_alignments, Iterable):
        rows = list(row_alignments)
    else:
        rows = [row_alignments] * len(strs_table)
    return _str_table(strs_table, cols, rows)
