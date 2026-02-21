Todo Manager CLI Template
=========================

This repository contains a small todo manager implemented with plain Python
scripts that store tasks in an XLS file. The project organizes command
implementations into `commands/` and keeps daily XLS files in `data/` at the
repo root. The CLI entrypoint is `commands/cli.py` and a tiny installed
wrapper (`todo`) can be used to run it.

Layout
- `commands/` — command wrappers and the CLI entrypoint (`commands/cli.py`).
- `data/` — daily XLS files are stored here (one file per day named
  `todos-DD-MM-YYYY.xls`).

INSTALLATION
------------
1) Clone the repository:

   git clone <repo-url> && cd todos

2) (Optional) Install the tiny wrapper that calls the CLI. By default the
   Makefile writes a small `todo` script into `$HOME/.local/bin` so you can
   run `todo ...` directly. To install run:

   make install

   If you don't want to use `make`, you can call the CLI directly with

   python3 -m commands.cli <command> <args>

3) Ensure `$HOME/.local/bin` is on your PATH if you installed the wrapper:

   export PATH="$HOME/.local/bin:$PATH"

USAGE
-----
After cloning (or after running `make install`) you can run the following
commands. Commands are case-insensitive — project codes and todo codes will
be normalized to UPPERCASE by the wrappers.

1) Initialize today's todo file (creates `data/todos-DD-MM-YYYY.xls`):

   todo init

   or

   python3 -m commands.cli init

2) Add a todo (format: `add <PROJ> <title>` — `PROJ` is the 3-letter
   project code; sequence numbers are generated automatically):

   todo add ABC "Write unit tests"

   Result example: `Added: ABC-001 - Write unit tests`

3) List todos for a project or all todos:

   todo list            # list all todos
   todo list ABC        # list todos for project ABC

4) Start / Pause / Continue / Complete:

   todo start ABC-001
   todo pause ABC-001
   todo pause all
   todo complete ABC-001

5) Show, delete:

   todo show ABC-001    # prints the todo with required fields (one per line)
   todo delete ABC-001

Notes
- The data files live in `data/` at the repo root; the CLI operates on
  today's file (based on the current date). The wrappers temporarily change
  CWD to the data directory when calling existing implementations, so the
  original scripts which build the filename from CWD continue to work.
If you prefer tests or packaging (console_scripts) instead of the Makefile
installer, I can help with that next.

Running tests
-------------
These tests use pytest. To run them locally:

1) Install test requirements (pytest, xlrd):

   pip install pytest xlrd

2) Run tests from the repo root:

   pytest -q
