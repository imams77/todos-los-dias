#!/usr/bin/env python3
import xlrd
from datetime import datetime
import os


def show_todo(code):
    today = datetime.now()
    filename = f"todos-{today.strftime('%d-%m-%Y')}.xls"
    if not os.path.exists(filename):
        return "Todo file for today not found. Run 'init for today' first."

    wb = xlrd.open_workbook(filename)
    ws = wb.sheet_by_name('Todos')

    row_found = None
    for row in range(1, ws.nrows):
        if ws.cell_value(row, 0) == code:
            row_found = row
            break

    if row_found is None:
        return "not exist"

    out = [code]
    def v(col):
        return ws.cell_value(row_found, col) if ws.ncols > col else ''

    mapping = [
        ('title', 1),
        ('status', 2),
        ('created at', 3),
        ('started at', 4),
        ('paused at', 7),
        ('continued at', 8),
        ('ended at', 5),
        ('duration', 6),
    ]

    for name, col in mapping:
        val = v(col)
        if val not in (None, ''):
            # Format duration value as HH:MM:SS if possible
            if name == 'duration':
                try:
                    try:
                        from .core.todo_ops import safe_float, format_seconds_as_hms
                    except Exception:
                        from commands.core.todo_ops import safe_float, format_seconds_as_hms

                    if isinstance(val, (int, float)):
                        out.append(f"{name}: {format_seconds_as_hms(float(val))}")
                    elif isinstance(val, str) and ':' in val:
                        out.append(f"{name}: {val}")
                    else:
                        secs = safe_float(val)
                        out.append(f"{name}: {format_seconds_as_hms(secs)}")
                    continue
                except Exception:
                    # fall back to raw value on any error
                    pass
            out.append(f"{name}: {val}")

    return "\n".join(out)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: show_todo.py <CODE>')
    else:
        print(show_todo(sys.argv[1]))
