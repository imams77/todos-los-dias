#!/usr/bin/env python3
"""Continue a paused todo using shared helpers."""
from datetime import datetime
import os

from .core.todo_ops import find_row_by_code, _parse_dt, safe_float, write_updated_file


def continue_todo(code):
    today = datetime.now()
    filename = f"todos-{today.strftime('%d-%m-%Y')}.xls"
    if not os.path.exists(filename):
        return f"Todo file for today not found. Run 'init for today' first."

    wb, ws, row_to_update = find_row_by_code(filename, code)
    if row_to_update is None:
        return f"Todo {code} not found"

    current_status = ws.cell_value(row_to_update, 2) if ws.ncols > 2 else ''
    if current_status != 'PAUSED':
        return f"Todo {code} is not paused"

    paused_at = ws.cell_value(row_to_update, 7) if ws.ncols > 7 else ''
    if not paused_at:
        return f"Todo {code} has no paused at timestamp"

    paused_dt = _parse_dt(paused_at)
    if not paused_dt:
        return f"Todo {code} has invalid paused at timestamp"

    # When continuing we must NOT add the paused interval to the duration.
    # The duration up to the pause has already been accumulated by the pause
    # action. Continue should just set status -> IN PROGRESS and record
    # continued_at (and clear paused_at).
    try:
        from .core.todo_ops import safe_float, format_seconds_as_hms
    except Exception:
        from commands.core.todo_ops import safe_float, format_seconds_as_hms
    existing_duration = safe_float(ws.cell_value(row_to_update, 6) if ws.ncols > 6 else 0.0)

    # Do not alter the recorded paused_at value; keep it for history.
    updates = {
        2: 'IN PROGRESS',
        6: format_seconds_as_hms(existing_duration) if existing_duration else '',
        8: today.strftime('%d/%m/%Y %H:%M:%S'),
    }
    write_updated_file(filename, row_to_update, updates, today)
    return f"Continued: {code}"


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: continue_todo.py <CODE>')
    else:
        print(continue_todo(sys.argv[1]))
