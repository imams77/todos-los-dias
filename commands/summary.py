#!/usr/bin/env python3
"""Implementation for displaying todo summary."""
import xlrd
import os
from datetime import datetime, timedelta
from .core.todo_ops import safe_float, format_seconds_as_hms


def get_filename(date=None):
    """Get the filename for the given date (default: today)."""
    if date is None:
        date = datetime.now()
    filename = f"todos-{date.strftime('%d-%m-%Y')}.xls"
    
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
    
    return filename


def summarize(date=None):
    """Return summary dict for the given date."""
    if date is None:
        date = datetime.now()
    
    filename = get_filename(date)
    
    if not os.path.exists(filename):
        return None
    
    wb = xlrd.open_workbook(filename)
    ws = wb.sheet_by_name('Todos')
    
    total = 0
    draft = 0
    in_progress = 0
    completed = 0
    completed_durations = []
    
    for row in range(1, ws.nrows):
        total += 1
        status = ws.cell_value(row, 2).upper() if ws.ncols > 2 else ''
        
        if status == 'DRAFT':
            draft += 1
        elif status == 'IN PROGRESS':
            in_progress += 1
        elif status == 'COMPLETED':
            completed += 1
            # collect duration
            if ws.ncols > 6:
                dur = ws.cell_value(row, 6)
                if dur not in (None, ''):
                    secs = safe_float(dur)
                    completed_durations.append(secs)
        elif status == 'PAUSED':
            pass  # paused doesn't count as started or draft
    
    started = in_progress + completed
    
    if started > 0:
        percent = (completed / started) * 100
    else:
        percent = 0.0
    
    avg_duration = None
    total_duration = None
    if completed_durations:
        avg_secs = sum(completed_durations) / len(completed_durations)
        avg_duration = format_seconds_as_hms(avg_secs)
        total_duration = format_seconds_as_hms(sum(completed_durations))
    
    return {
        'date': date.strftime('%d/%m/%Y'),
        'total': total,
        'draft': draft,
        'started': started,
        'in_progress': in_progress,
        'completed': completed,
        'percent': percent,
        'avg_duration': avg_duration,
        'total_duration': total_duration,
    }


def print_summary(date=None):
    """Print summary for the given date."""
    if date is None:
        date = datetime.now()
    
    summary = summarize(date)
    
    if summary is None:
        if date.date() == datetime.now().date():
            print("No todo file for today found. Run 'init for today' first.")
        else:
            print(f"No todo file for {date.strftime('%d/%m/%Y')} found.")
        return
    
    print(f"date: {summary['date']}")
    print(f"total added: {summary['total']}")
    print(f"  draft (not started): {summary['draft']}")
    print(f"  started: {summary['started']}")
    print(f"    in progress: {summary['in_progress']}")
    print(f"  completed: {summary['completed']}")
    print(f"")
    print(f"percent done (completed / started): {summary['percent']:.1f}%")
    
    if summary['total_duration']:
        print(f"total time: {summary['total_duration']}")
    
    if summary['avg_duration']:
        print(f"average time per completed: {summary['avg_duration']}")
    
    # Suggestion if started but no completed
    if summary['started'] > 0 and summary['completed'] == 0:
        print(f"")
        print(f"You have started {summary['started']} task(s) but haven't completed any yet. Consider focusing on completing some of them before starting new ones.")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'yesterday':
        d = datetime.now() - timedelta(days=1)
        print_summary(d)
    else:
        print_summary()
