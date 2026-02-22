#!/usr/bin/env python3
"""Start (or continue) a todo.

This implementation delegates the shared XLS manipulation to the helper in
`commands.core.todo_ops` to avoid duplication with `continue_todo.py`.
"""
from datetime import datetime
import os

from .core.todo_ops import find_row_by_code, _parse_dt, safe_float, write_updated_file


def start_todo(code):
    today = datetime.now()
    filename = f"todos-{today.strftime('%d-%m-%Y')}.xls"
    if not os.path.exists(filename):
        return f"Todo file for today not found. Run 'init for today' first."

    wb, ws, row_to_update = find_row_by_code(filename, code)
    if row_to_update is None:
        return f"Todo {code} not found"

    current_status = ws.cell_value(row_to_update, 2) if ws.ncols > 2 else ''

    # If paused -> behave like continue: accumulate duration from paused_at
    if current_status == 'PAUSED':
        paused_at = ws.cell_value(row_to_update, 7) if ws.ncols > 7 else ''
        if not paused_at:
            return f"Todo {code} has no paused at timestamp"

        paused_dt = _parse_dt(paused_at)
        if not paused_dt:
            return f"Todo {code} has invalid paused at timestamp"

        # Resume behaviour: do NOT add the paused interval to the recorded
        # duration (the pause action already accumulated work up to paused_at).
        # Set status -> IN PROGRESS and record continued_at; keep paused_at for
        # history so we can see when the pause occurred.
        try:
            from .core.todo_ops import safe_float, format_seconds_as_hms
        except Exception:
            from commands.core.todo_ops import safe_float, format_seconds_as_hms
        existing_duration = safe_float(ws.cell_value(row_to_update, 6) if ws.ncols > 6 else 0.0)

        updates = {
            2: 'IN PROGRESS',
            6: format_seconds_as_hms(existing_duration) if existing_duration else '',
            8: today.strftime('%d/%m/%Y %H:%M:%S'),
        }
        write_updated_file(filename, row_to_update, updates, today)
        return f"Continued: {code}"

    # Otherwise set started_at and status
    updates = {
        2: 'IN PROGRESS',
        4: today.strftime('%d/%m/%Y %H:%M:%S'),
    }
    write_updated_file(filename, row_to_update, updates, today)
    return f"Started: {code}"


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: start_todo.py <CODE>')
    else:
        print(start_todo(sys.argv[1]))
