"""
sudoku_solver.py
----------------
A console‑based Sudoku assistant/solver written for an undergraduate Python course.

Features
~~~~~~~~
* Calculates valid options for each empty cell according to Sudoku rules.
* Automatically fills in cells that have a single possible digit.
* Detects invalid boards or boards that reach an unsolvable state.
* Allows the user to choose digits when multiple options exist (interactive CLI).
* Can generate a random partially‑filled board.
* Writes final board states and results to `solved_sudoku.txt`.

Usage
~~~~~
$ python sudoku_solver.py

Dependencies: only the Python standard library.
"""

import random
from typing import List, Tuple
import boards

# ---------- Constants --------------------------------------------------------

NOT_FINISH = "NOT_FINISH"
FINISH_SUCCESS = "FINISH_SUCCESS"
FINISH_FAILURE = "FINISH_FAILURE"

# ---------- Helper functions -------------------------------------------------


def option_in_part(row: List[int]) -> List[int]:
    """Return all digits 1‑9 that *do not* appear in the given 9‑element list."""
    return [num for num in range(1, 10) if num not in row]


def options(sudoku_board: List[List[int]], loc: Tuple[int, int]) -> List[int]:
    """
    Compute all valid digits for a given (row, col) *loc* on *sudoku_board*.
    `-1` represents an empty cell; if the cell is already filled the result is [].
    """
    r, c = loc
    if sudoku_board[r][c] != -1:
        return []

    # Row + column candidates
    opts_row = option_in_part(sudoku_board[r])
    opts_col = option_in_part([sudoku_board[i][c] for i in range(9)])

    # 3×3 square candidates
    square_vals = []
    r0, c0 = 3 * (r // 3), 3 * (c // 3)
    for i in range(r0, r0 + 3):
        for j in range(c0, c0 + 3):
            square_vals.append(sudoku_board[i][j])
    opts_square = option_in_part(square_vals)

    # Intersection of all three sets
    return [n for n in opts_square if n in opts_row and n in opts_col]


def possible_digits(sudoku_board: List[List[int]]) -> List[List[List[int] | None]]:
    """Return a 9×9 grid mirroring *sudoku_board* with option lists / None."""
    board_opts = []
    for r in range(9):
        row_opts = []
        for c in range(9):
            row_opts.append(options(sudoku_board, (r, c)) if sudoku_board[r][c] == -1 else None)
        board_opts.append(row_opts)
    return board_opts


def check_final_board(sudoku_board: List[List[int]]) -> bool:
    """True if there are no empty cells (-1) on the board."""
    return all(cell != -1 for row in sudoku_board for cell in row)


def check_part_for_failure(part: List[int]) -> bool:
    """True if *part* (row / column / square) violates Sudoku uniqueness."""
    return any(part.count(num) > 1 and num != -1 for num in range(9))


def is_board_failure(sudoku_board: List[List[int]]) -> bool:
    """Validate entire board; True indicates a rule violation."""
    # Rows + columns
    for i in range(9):
        if check_part_for_failure(sudoku_board[i]) or            check_part_for_failure([sudoku_board[r][i] for r in range(9)]):
            return True

    # 3×3 squares
    for r0 in range(0, 9, 3):
        for c0 in range(0, 9, 3):
            square = [sudoku_board[r][c]
                      for r in range(r0, r0 + 3)
                      for c in range(c0, c0 + 3)]
            if check_part_for_failure(square):
                return True
    return False


def possible_continuation(possibilities: List[List[List[int] | None]]) -> bool:
    """True if at least one cell has exactly *one* possible digit."""
    return any(opt is not None and len(opt) == 1
               for row in possibilities for opt in row)


def find_least_options(possibilities: List[List[List[int] | None]]) -> Tuple[int, int] | None:
    """Return coordinates of the cell with the fewest (>0) options."""
    min_len, min_loc = 10, None
    for r in range(9):
        for c in range(9):
            opts = possibilities[r][c]
            if opts is not None and 0 < len(opts) < min_len:
                min_len, min_loc = len(opts), (r, c)
    return min_loc


def is_out_of_options(possibilities: List[List[List[int] | None]]) -> bool:
    """True if some empty cell has zero valid digits."""
    return any(opt is not None and len(opt) == 0
               for row in possibilities for opt in row)

# ---------- Core solving routines -------------------------------------------


def one_stage(sudoku_board: List[List[int]],
              possibilities: List[List[List[int] | None]]) -> Tuple[str, Tuple[int, int]]:
    """
    Attempt to progress one logical step.

    Returns (state, loc):
        * FINISH_FAILURE, (-1, -1)   – invalid board or contradiction
        * FINISH_SUCCESS, (10, 10)   – board completely solved
        * NOT_FINISH, (r, c)         – need user input at (r, c)
    """
    while True:
        if is_board_failure(sudoku_board) or is_out_of_options(possibilities):
            return FINISH_FAILURE, (-1, -1)

        if check_final_board(sudoku_board):
            return FINISH_SUCCESS, (10, 10)

        if not possible_continuation(possibilities):
            loc = find_least_options(possibilities)
            return NOT_FINISH, loc

        # Fill any cell with a single candidate
        updated = False
        for r in range(9):
            for c in range(9):
                opts = possibilities[r][c]
                if opts is not None and len(opts) == 1:
                    sudoku_board[r][c] = opts[0]
                    possibilities[r][c] = None
                    updated = True
        if not updated:
            # No automatic progress possible
            loc = find_least_options(possibilities)
            return NOT_FINISH, loc


def fill_board(sudoku_board: List[List[int]],
               possibilities: List[List[List[int] | None]]) -> str:
    """
    Interactive loop that repeatedly calls `one_stage`.
    The user is asked to choose a value whenever multiple options exist.
    """
    state = NOT_FINISH
    while state == NOT_FINISH:
        state, loc = one_stage(sudoku_board, possibilities)
        if state == NOT_FINISH and loc:
            r, c = loc
            cell_options = possibilities[r][c]
            sudoku_board[r][c] = 0  # temporary placeholder for display
            print_board(sudoku_board)
            print("Options for cell (%d, %d): %s" % (r + 1, c + 1, cell_options))
            choice = None
            while choice not in cell_options:
                try:
                    choice = int(input("Choose your option: "))
                except ValueError:
                    continue
            sudoku_board[r][c] = choice
            possibilities = possible_digits(sudoku_board)
    return state


def create_random_board(sudoku_board: List[List[int]]) -> None:
    """
    Fill *N* random positions (10–19) on an empty board with legal digits.
    """
    N = random.randrange(10, 20)
    positions = [(r, c) for r in range(9) for c in range(9)]
    filled = 0
    while filled < N and positions:
        idx = random.randrange(len(positions))
        r, c = positions.pop(idx)
        if sudoku_board[r][c] == -1:
            opts = options(sudoku_board, (r, c))
            if opts:
                sudoku_board[r][c] = random.choice(opts)
                filled += 1


def print_board(sudoku_board: List[List[int]]) -> None:
    """Pretty‑print the current state to the console."""
    sep = "+---" * 9 + "+"
    print(sep)
    for r, row in enumerate(sudoku_board):
        line = "|".join(" %d " % n if n != -1 else "   " for n in row)
        print("|" + line + "|")
        if (r + 1) % 3 == 0:
            print(sep)


def print_board_to_file(sudoku_board: List[List[int]], file_name: str) -> None:
    """Append the board to *file_name* in a readable text format."""
    with open(file_name, "a", encoding="utf-8") as f:
        f.write("+---" * 9 + "+\n")
        for r, row in enumerate(sudoku_board):
            line = "|".join(f" {n} " if n != -1 else "   " for n in row)
            f.write("|" + line + "|\n")
            if (r + 1) % 3 == 0:
                f.write("+---" * 9 + "+\n")


# ---------- Script entry point ----------------------------------------------


def main() -> None:
    # Prepare boards (copy so originals remain unmodified)
    board_list = [
        [row[:] for row in boards.EXAMPLE_BOARD],
        [row[:] for row in boards.PERFECT_BOARD],
        [row[:] for row in boards.IMPOSSIBLE_BOARD],
        [row[:] for row in boards.BUG_BOARD],
        [row[:] for row in boards.INTERESTING_BOARD],
    ]
    create_random_board(board_list[-1])  # add randomness to the last board

    # Reset log file
    with open("solved_sudoku.txt", "w", encoding="utf-8"):
        pass

    # Solve / play each board
    for idx, board in enumerate(board_list, 1):
        print(f"\n=== Board {idx} ===")
        possibilities = possible_digits(board)
        result = fill_board(board, possibilities)

        with open("solved_sudoku.txt", "a", encoding="utf-8") as f:
            f.write(result + "\n")
        print_board_to_file(board, "solved_sudoku.txt")
        print(f"Result: {result}")


if __name__ == "__main__":
    main()
