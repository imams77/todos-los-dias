#!/usr/bin/env python3
"""Continue all todos with status PAUSED."""
import xlrd
import xlwt
from datetime import datetime
import os


def continue_all_todos():
    today = datetime.now()
    filename = f"todos-{today.strftime('%d-%m-%Y')}.xls"
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

    continued_codes = []
    rows_to_update = []
    
    for row in range(1, ws.nrows):
        status = ws.cell_value(row, 2).upper() if ws.ncols > 2 else ''
        if status == 'PAUSED':
            code = ws.cell_value(row, 0)
            continued_codes.append(code)
            rows_to_update.append(row)

    if not continued_codes:
        return "No paused todos to continue"

    try:
        from .core.todo_ops import safe_float, format_seconds_as_hms
    except Exception:
        from commands.core.todo_ops import safe_float, format_seconds_as_hms

    updates = {}
    for row in rows_to_update:
        paused_at = ws.cell_value(row, 7) if ws.ncols > 7 else ''
        
        added_seconds = 0.0
        if paused_at:
            try:
                paused_dt = datetime.strptime(paused_at, '%d/%m/%Y %H:%M:%S')
                added_seconds = (today - paused_dt).total_seconds()
            except Exception:
                added_seconds = 0.0

        existing_duration = safe_float(ws.cell_value(row, 6) if ws.ncols > 6 else 0.0)
        total_duration = existing_duration + added_seconds
        
        updates[row] = {
            'status': 'IN PROGRESS',
            'duration': format_seconds_as_hms(total_duration),
            'continued_at': today.strftime('%d/%m/%Y %H:%M:%S'),
        }

    wb_write = xlwt.Workbook()
    ws_write = wb_write.add_sheet('Todos')
    ws_projects_write = wb_write.add_sheet('Project List')

    headers = ['code', 'title', 'status', 'created at', 'started at', 'ended at', 'duration', 'paused at', 'continued at']
    for i, h in enumerate(headers):
        ws_write.write(0, i, h)

    for row in range(1, ws.nrows):
        for col in range(ws.ncols):
            val = ws.cell_value(row, col)
            
            if row in updates:
                if col == 2:
                    val = updates[row]['status']
                elif col == 6:
                    val = updates[row]['duration']
                elif col == 8:
                    val = updates[row]['continued_at']
            
            ws_write.write(row, col, val)

    wb_projects = xlrd.open_workbook(filename)
    ws_projects = wb_projects.sheet_by_name('Project List')
    ws_projects_write.write(0, 0, 'Project Code')
    for row in range(1, ws_projects.nrows):
        ws_projects_write.write(row, 0, ws_projects.cell_value(row, 0))

    wb_write.save(filename)
    return f"Continued {len(continued_codes)} todo(s): {', '.join(continued_codes)}"


if __name__ == '__main__':
    print(continue_all_todos())
