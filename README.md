# Sudoku Solver (CLI)

University project – **Python console application** that analyses and solves Sudoku puzzles while letting the user intervene when multiple options exist.

## Features

* Calculates allowed digits for every empty cell (`-1`).
* Automatically fills cells with a single possible digit.
* Detects invalid boards and impossible states.
* Interactive: asks the user to choose when several digits fit.
* Can generate a random starting board.
* Logs board states and results to `solved_sudoku.txt`.

## File overview

| File | Purpose |
|------|---------|
| `boards.py` | Sample boards used for testing (feel free to replace). |
| `sudoku_solver.py` | Main script with all solving logic and CLI. |
| `solved_sudoku.txt` | Output file created at runtime. |

## Running

```bash
python sudoku_solver.py
```

The script will iterate over several test boards, attempt to solve each one,
and prompt you for input when necessary.

## Requirements

* Python 3.9 or newer  
* No external libraries needed


