#!/usr/bin/env python3
import xlrd
from datetime import datetime
import os


def show_todo(code):
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

        # Special handling for duration: compute or format the duration even if
        # the stored cell is empty (useful for IN PROGRESS tasks).
        if name == 'duration':
            try:
                try:
                    from .core.todo_ops import safe_float, format_seconds_as_hms
                except Exception:
                    from commands.core.todo_ops import safe_float, format_seconds_as_hms

                status = v(2)
                try:
                    status_up = str(status).strip().upper() if status not in (None, '') else ''
                except Exception:
                    status_up = ''

                # base seconds from stored duration (handles HH:MM:SS or numeric)
                try:
                    base_secs = safe_float(val) if val not in (None, '') else 0.0
                except Exception:
                    base_secs = 0.0

                result_secs = None

                if status_up == 'IN PROGRESS':
                    # prefer continued_at (col 8) then started_at (col 4)
                    tstr = v(8) or ''
                    if not tstr:
                        tstr = v(4) or ''
                    added = 0.0
                    if tstr:
                        try:
                            started_dt = datetime.strptime(tstr, '%d/%m/%Y %H:%M:%S')
                            added = (datetime.now() - started_dt).total_seconds()
                            if added < 0:
                                added = 0.0
                        except Exception:
                            added = 0.0
                    result_secs = (base_secs or 0.0) + (added or 0.0)

                elif status_up == 'PAUSED':
                    # If stored duration exists use it; otherwise compute the
                    # segment from continued/started to paused and add to base.
                    if val not in (None, ''):
                        result_secs = base_secs
                    else:
                        tpause = v(7) or ''
                        tstart = v(8) or v(4) or ''
                        added = 0.0
                        if tpause and tstart:
                            try:
                                paused_dt = datetime.strptime(tpause, '%d/%m/%Y %H:%M:%S')
                                started_dt = datetime.strptime(tstart, '%d/%m/%Y %H:%M:%S')
                                added = (paused_dt - started_dt).total_seconds()
                                if added < 0:
                                    added = 0.0
                            except Exception:
                                added = 0.0
                        result_secs = (base_secs or 0.0) + (added or 0.0)

                elif status_up == 'COMPLETED':
                    if val not in (None, ''):
                        result_secs = base_secs
                    else:
                        tstart = v(4) or ''
                        tend = v(5) or ''
                        if tstart and tend:
                            try:
                                start_dt = datetime.strptime(tstart, '%d/%m/%Y %H:%M:%S')
                                end_dt = datetime.strptime(tend, '%d/%m/%Y %H:%M:%S')
                                secs = (end_dt - start_dt).total_seconds()
                                if secs < 0:
                                    secs = 0.0
                                result_secs = secs
                            except Exception:
                                result_secs = None
                        else:
                            result_secs = None

                else:
                    # DRAFT or unknown status: only show if stored value exists
                    if val not in (None, ''):
                        result_secs = base_secs

                if result_secs is not None:
                    out.append(f"{name}: {format_seconds_as_hms(result_secs)}")
                # otherwise skip showing duration
                continue
            except Exception:
                # fall back to raw value on any error
                pass

        if val not in (None, ''):
            out.append(f"{name}: {val}")

    return "\n".join(out)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: show_todo.py <CODE>')
    else:
        print(show_todo(sys.argv[1]))
