# Todos Los Dias

"Todos los dias" means "Every day" in Spanish. 
This project helps you track your daily tasks.

This repository contains a small todo manager implemented with plain Python
scripts that store tasks in an XLS file. The project organizes command
implementations into `commands/` and keeps daily XLS files in `data/` at the
repo root. The CLI entrypoint is `commands/cli.py` and a tiny installed
wrapper (`todo`) can be used to run it.

Layout

- `commands/` — command wrappers and the CLI entrypoint (`commands/cli.py`).
- `data/` — daily XLS files are stored here (one file per day named
  `todos-DD-MM-YYYY.xls`).

## INSTALLATION

1. Clone the repository:

   git clone git@github.com:imams77/todos-los-dias.git && cd todos-los-dias

2. (Optional) Install the tiny wrapper that calls the CLI. By default the
   Makefile writes a small `todo` script into `$HOME/.local/bin` so you can
   run `todo ...` directly. To install run:

   make install

   If you don't want to use `make`, you can call the CLI directly with

   python3 -m commands.cli <command> <args>

3. Ensure `$HOME/.local/bin` is on your PATH if you installed the wrapper:

   export PATH="$HOME/.local/bin:$PATH"

## USAGE

After cloning (or after running `make install`) you can run the following
commands. Commands are case-insensitive — project codes and todo codes will
be normalized to UPPERCASE by the wrappers.

1. Initialize today's todo file (creates `data/todos-DD-MM-YYYY.xls`):

   todo init

   or

   python3 -m commands.cli init

2. Add a todo (format: `add <PROJ> <title>` — `PROJ` is the 3-letter
   project code; sequence numbers are generated automatically):

   todo add ABC "Write unit tests"

   Result example: `Added: ABC-001 - Write unit tests`

3. List todos for a project or all todos:

   todo list # list all todos
   todo list ABC # list todos for project ABC

4. Start / Pause / Continue / Complete:

   todo start ABC-001
   todo pause ABC-001
   todo pause all
   todo complete ABC-001

5. Show, delete:

   todo show ABC-001 # prints the todo with required fields (one per line)
   todo delete ABC-001

Notes

- The data files live in `data/` at the repo root; the CLI operates on
  today's file (based on the current date). The wrappers temporarily change
  CWD to the data directory when calling existing implementations, so the
  original scripts which build the filename from CWD continue to work.
  If you prefer tests or packaging (console_scripts) instead of the Makefile
  installer, I can help with that next.

## Usage with AI

---

The CLI can be used with an AI agent. The agent can run the `todo` command with the specified arguments to manage todos. For example, an agent could be programmed to automatically add todos based on user input or to list todos when requested.
You can use (https://opencode.ai/)[opencode] for running the AI from command line.

### Changing AI behavior

To change the behavior of the AI agent, you can modify the AGENTS.md file.

## Running tests

These tests use pytest. To run them locally:

1. Install test requirements (pytest, xlrd):

   pip install pytest xlrd

2. Run tests from the repo root:

   pytest -q

## Upcoming Features in order

### Basic Features

- [ ] Determine what to do to `IN PROGRESS` tasks if the day changed.
- [ ] Add a `todo edit [code] [field_name] [new_value]` command to edit the title of an existing todo.
- [ ] Implement a `todo search [query]` command to search for todos by title or project code.
- [ ] Add a `todo list [field_name] [status]` option to list only completed todos. field name can be `status` or `project (3 digits code)`.
- [ ] Add a `todo global` command to run search / list across all files (e.g. search for a todo across all days).

### Sprint system

- [ ] Implement sprint features, which will create a folder for each sprint and store todos in a sprint-specific file.
- [ ] Add import/export functionality to add bulk todos to a sprint (e.g. CSV). And the import template.
- [ ] Add story points or priority levels to todos.
- [ ] Implement a `todo velocity` command to calculate velocity based on completed todos.
