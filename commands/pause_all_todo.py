#!/usr/bin/env python3
"""Pause all todos with status IN PROGRESS."""
import xlrd
import xlwt
from datetime import datetime
import os


def pause_all_todos():
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

    paused_codes = []
    rows_to_update = []
    
    for row in range(1, ws.nrows):
        status = ws.cell_value(row, 2).upper() if ws.ncols > 2 else ''
        if status == 'IN PROGRESS':
            code = ws.cell_value(row, 0)
            paused_codes.append(code)
            rows_to_update.append(row)

    if not paused_codes:
        return "No todos in progress to pause"

    try:
        from .core.todo_ops import safe_float, format_seconds_as_hms
    except Exception:
        from commands.core.todo_ops import safe_float, format_seconds_as_hms

    updates = {}
    for row in rows_to_update:
        added_seconds = 0.0
        time_str = ''
        if ws.ncols > 8:
            time_str = ws.cell_value(row, 8) or ''
        if not time_str and ws.ncols > 4:
            time_str = ws.cell_value(row, 4) or ''

        if time_str:
            try:
                started_dt = datetime.strptime(time_str, '%d/%m/%Y %H:%M:%S')
                added_seconds = (today - started_dt).total_seconds()
            except Exception:
                added_seconds = 0.0

        existing_duration = safe_float(ws.cell_value(row, 6) if ws.ncols > 6 else 0.0)
        total_duration = existing_duration + added_seconds
        
        updates[row] = {
            'status': 'PAUSED',
            'duration': format_seconds_as_hms(total_duration),
            'paused_at': today.strftime('%d/%m/%Y %H:%M:%S'),
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
                elif col == 7:
                    val = updates[row]['paused_at']
            
            ws_write.write(row, col, val)

    wb_projects = xlrd.open_workbook(filename)
    ws_projects = wb_projects.sheet_by_name('Project List')
    ws_projects_write.write(0, 0, 'Project Code')
    for row in range(1, ws_projects.nrows):
        ws_projects_write.write(row, 0, ws_projects.cell_value(row, 0))

    wb_write.save(filename)
    return f"Paused {len(paused_codes)} todo(s): {', '.join(paused_codes)}"


if __name__ == '__main__':
    print(pause_all_todos())
