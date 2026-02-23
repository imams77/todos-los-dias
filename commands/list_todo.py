#!/usr/bin/env python3
import xlrd
from datetime import datetime
import os
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.text import Text


console = Console()


def list_todos(code=None, status=None):
    try:
        from .core.todo_ops import safe_float, format_seconds_as_hms
    except Exception:
        from commands.core.todo_ops import safe_float, format_seconds_as_hms
    
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
        print("Todo file for today not found. Run 'init for today' first.")
        return

    wb = xlrd.open_workbook(filename)
    ws = wb.sheet_by_name('Todos')

    table = Table(box=box.SIMPLE)
    table.add_column("Code", style="cyan")
    table.add_column("Title")
    table.add_column("Status", style="magenta")
    table.add_column("Duration", justify="right", style="green")

    rows_data = []

    for row in range(1, ws.nrows):
        row_code = ws.cell_value(row, 0)
        if code:
            if '-' in code:
                if row_code != code:
                    continue
            else:
                if not row_code.startswith(code + '-'):
                    continue
        if status:
            cur = ws.cell_value(row, 2) if ws.ncols > 2 else ''
            if cur.upper() != status.upper():
                continue

        title = ws.cell_value(row, 1) if ws.ncols > 1 else ''
        st = ws.cell_value(row, 2) if ws.ncols > 2 else ''
        raw_duration = ws.cell_value(row, 6) if ws.ncols > 6 else ''
        
        if raw_duration in (None, ''):
            duration = ''
        else:
            try:
                if isinstance(raw_duration, str) and ':' in raw_duration:
                    duration = raw_duration
                else:
                    secs = safe_float(raw_duration)
                    duration = format_seconds_as_hms(secs)
            except Exception:
                duration = str(raw_duration)

        rows_data.append((row_code, title, st, duration))

    for row_code, title, st, duration in rows_data:
        table.add_row(row_code, title, st, duration)

    console.print(table)
    _print_summary(ws, code, status)


def _print_summary(ws, code_filter, status_filter):
    """Print a summary footer with counts."""
    total = 0
    draft = 0
    in_progress = 0
    completed = 0
    paused = 0
    
    for row in range(1, ws.nrows):
        row_code = ws.cell_value(row, 0)
        if code_filter:
            if '-' in code_filter:
                if row_code != code_filter:
                    continue
            else:
                if not row_code.startswith(code_filter + '-'):
                    continue
        
        status = ws.cell_value(row, 2).upper() if ws.ncols > 2 else ''
        if status_filter and status != status_filter.upper():
            continue
            
        total += 1
        if status == 'DRAFT':
            draft += 1
        elif status == 'IN PROGRESS':
            in_progress += 1
        elif status == 'COMPLETED':
            completed += 1
        elif status == 'PAUSED':
            paused += 1
    
    print("")
    # Using rich for styled summary
    summary_text = Text()
    summary_text.append(f"Total: {total}  ", style="bold white")
    summary_text.append(f"DRAFT: {draft}  ", style="yellow")
    summary_text.append(f"IN PROGRESS: {in_progress}  ", style="blue")
    summary_text.append(f"PAUSED: {paused}  ", style="orange3")
    summary_text.append(f"COMPLETED: {completed}", style="green")
    console.print(Panel(summary_text, border_style="dim"))


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        list_todos()
    elif len(sys.argv) == 2:
        list_todos(sys.argv[1])
    else:
        list_todos(sys.argv[1], ' '.join(sys.argv[2:]))
