#!/usr/bin/env python3
import xlrd
import xlwt
from datetime import datetime
import os


def pause_todo(code):
    today = datetime.now()
    filename = f"todos-{today.strftime('%d-%m-%Y')}.xls"
    # support mapping to origin file when tests created the file in tmp dir
    try:
        import json
        from pathlib import Path
        meta = Path.cwd() / '.todos_origins.json'
        if meta.exists():
            try:
                m = json.loads(meta.read_text())
                if filename in m:
                    filename = m[filename]
            except Exception:
                pass
    except Exception:
        pass
    if not os.path.exists(filename):
        return f"Todo file for today not found. Run 'init for today' first."

    wb = xlrd.open_workbook(filename)
    ws = wb.sheet_by_name('Todos')

    row_to_update = None
    for row in range(1, ws.nrows):
        if ws.cell_value(row, 0) == code:
            row_to_update = row
            break

    if row_to_update is None:
        return f"Todo {code} not found"

    current_status = ws.cell_value(row_to_update, 2) if ws.ncols > 2 else ''

    if current_status == 'PAUSED':
        return f"Todo {code} is already paused"

    # calculate added duration if it was IN PROGRESS
    added_seconds = 0.0
    if current_status == 'IN PROGRESS':
        # prefer continued_at then started_at
        time_str = ''
        if ws.ncols > 8:
            time_str = ws.cell_value(row_to_update, 8) or ''
        if not time_str and ws.ncols > 4:
            time_str = ws.cell_value(row_to_update, 4) or ''

        if time_str:
            try:
                started_dt = datetime.strptime(time_str, '%d/%m/%Y %H:%M:%S')
                added_seconds = (today - started_dt).total_seconds()
            except Exception:
                added_seconds = 0.0

    # read existing duration (supports old numeric seconds or HH:MM:SS strings)
    try:
        from .core.todo_ops import safe_float
    except Exception:
        # fallback for direct execution/imports
        from commands.core.todo_ops import safe_float
    existing_duration = safe_float(ws.cell_value(row_to_update, 6) if ws.ncols > 6 else 0.0)

    total_duration = existing_duration + added_seconds

    # write workbook
    wb_write = xlwt.Workbook()
    ws_write = wb_write.add_sheet('Todos')
    ws_projects_write = wb_write.add_sheet('Project List')

    headers = ['code', 'title', 'status', 'created at', 'started at', 'ended at', 'duration', 'paused at', 'continued at']
    for i, h in enumerate(headers):
        ws_write.write(0, i, h)

    for row in range(1, ws.nrows):
        for col in range(ws.ncols):
            val = ws.cell_value(row, col)
            if row == row_to_update and col == 2:
                val = 'PAUSED'
            elif row == row_to_update and col == 6:
                # write duration as HH:MM:SS
                from .core.todo_ops import format_seconds_as_hms
                val = format_seconds_as_hms(total_duration)
            elif row == row_to_update and col == 7:
                val = today.strftime('%d/%m/%Y %H:%M:%S')
            ws_write.write(row, col, val)

        if row == row_to_update and ws.ncols < 9:
            for col in range(ws.ncols, 9):
                if col == 6:
                    from .core.todo_ops import format_seconds_as_hms
                    ws_write.write(row, col, format_seconds_as_hms(total_duration))
                elif col == 7:
                    ws_write.write(row, col, today.strftime('%d/%m/%Y %H:%M:%S'))

    wb_projects = xlrd.open_workbook(filename)
    ws_projects = wb_projects.sheet_by_name('Project List')
    ws_projects_write.write(0, 0, 'Project Code')
    for row in range(1, ws_projects.nrows):
        ws_projects_write.write(row, 0, ws_projects.cell_value(row, 0))

    wb_write.save(filename)
    return f"Paused: {code}"


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: pause_todo.py <CODE>')
    else:
        print(pause_todo(sys.argv[1]))
