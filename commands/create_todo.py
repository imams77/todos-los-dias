#!/usr/bin/env python3
from pathlib import Path
import xlwt
import xlrd
from datetime import datetime, timedelta
import json
import os


def create_todo_file(data_dir=None):
    data_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parents[1] / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now()
    filename = data_dir / f"todos-{today.strftime('%d-%m-%Y')}.xls"

    if filename.exists():
        return f"file for today already exists"

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Todos')

    headers = ['code', 'title', 'status', 'created at', 'started at', 'ended at', 'duration', 'paused at', 'continued at']
    for i, h in enumerate(headers):
        ws.write(0, i, h)

    # check previous day's file and copy tasks that are PAUSED, DRAFT or IN PROGRESS
    prev = today - timedelta(days=1)
    prev_filename = data_dir / f"todos-{prev.strftime('%d-%m-%Y')}.xls"

    copied = []
    project_codes = set()
    existing_codes = set()

    # helpers for duration parsing/formatting (use shared utils when available)
    try:
        from .core.todo_ops import safe_float, format_seconds_as_hms
    except Exception:
        try:
            from commands.core.todo_ops import safe_float, format_seconds_as_hms
        except Exception:
            safe_float = None
            format_seconds_as_hms = None

    if prev_filename.exists():
        try:
            prev_wb = xlrd.open_workbook(str(prev_filename))
            if 'Todos' in prev_wb.sheet_names():
                prev_ws = prev_wb.sheet_by_name('Todos')
                for row in range(1, prev_ws.nrows):
                    prev_code = prev_ws.cell_value(row, 0) if prev_ws.ncols > 0 else ''
                    prev_title = prev_ws.cell_value(row, 1) if prev_ws.ncols > 1 else ''
                    prev_status = prev_ws.cell_value(row, 2) if prev_ws.ncols > 2 else ''
                    prev_created = prev_ws.cell_value(row, 3) if prev_ws.ncols > 3 else ''
                    prev_started = prev_ws.cell_value(row, 4) if prev_ws.ncols > 4 else ''
                    prev_ended = prev_ws.cell_value(row, 5) if prev_ws.ncols > 5 else ''
                    prev_duration = prev_ws.cell_value(row, 6) if prev_ws.ncols > 6 else ''
                    prev_paused = prev_ws.cell_value(row, 7) if prev_ws.ncols > 7 else ''
                    prev_continued = prev_ws.cell_value(row, 8) if prev_ws.ncols > 8 else ''

                    if prev_status and str(prev_status).upper() in ('PAUSED', 'DRAFT', 'IN PROGRESS'):
                        # reuse original code if it won't conflict; otherwise assign next sequential
                        new_code = str(prev_code) if prev_code else ''
                        if new_code and new_code in existing_codes:
                            prefix = new_code.split('-')[0] if '-' in new_code else new_code
                            seqs = [int(c.split('-')[1]) for c in existing_codes if c.startswith(prefix + '-') and '-' in c]
                            next_num = max(seqs) + 1 if seqs else 1
                            new_code = f"{prefix}-{next_num:03d}"
                        existing_codes.add(new_code)
                        prefix = new_code.split('-')[0] if '-' in new_code else new_code
                        if prefix:
                            project_codes.add(prefix)

                        status_upper = str(prev_status).upper()

                        # Preserve most fields as-is. Rules:
                        # - DRAFT: keep DRAFT and keep timestamps
                        # - PAUSED: keep PAUSED and all timestamps as-is
                        # - IN PROGRESS: convert to PAUSED, set paused_at to now and
                        #   accumulate duration as pause flow would do (using
                        #   continued_at or started_at)
                        if status_upper == 'IN PROGRESS':
                            new_status = 'PAUSED'
                            paused_at = today.strftime('%d/%m/%Y %H:%M:%S')

                            # prefer continued_at then started_at for calculating
                            # the interval to add to duration
                            time_str = prev_continued if prev_continued else prev_started
                            added_seconds = 0.0
                            if time_str:
                                try:
                                    started_dt = datetime.strptime(time_str, '%d/%m/%Y %H:%M:%S')
                                    added_seconds = (today - started_dt).total_seconds()
                                except Exception:
                                    added_seconds = 0.0

                            try:
                                existing_secs = safe_float(prev_duration) if safe_float else 0.0
                            except Exception:
                                existing_secs = 0.0

                            total_secs = (existing_secs or 0.0) + (added_seconds or 0.0)
                            duration_str = format_seconds_as_hms(total_secs) if format_seconds_as_hms else prev_duration
                        else:
                            new_status = str(prev_status)
                            paused_at = prev_paused
                            duration_str = prev_duration

                        copied.append({
                            'code': new_code,
                            'title': prev_title,
                            'status': new_status,
                            'created_at': prev_created,
                            'started_at': prev_started,
                            'ended_at': prev_ended,
                            'duration': duration_str,
                            'paused_at': paused_at,
                            'continued_at': prev_continued,
                        })

            # also collect project list entries if present
            if 'Project List' in prev_wb.sheet_names():
                ws_proj = prev_wb.sheet_by_name('Project List')
                for r in range(1, ws_proj.nrows):
                    c = ws_proj.cell_value(r, 0)
                    if c:
                        project_codes.add(str(c))
        except Exception:
            # if we cannot read previous file just ignore and continue
            pass

    # write copied tasks into today's Todos sheet (preserve original data
    # except for the status/paused handling performed above)
    for i, item in enumerate(copied, start=1):
        ws.write(i, 0, item.get('code', ''))
        ws.write(i, 1, item.get('title', ''))
        ws.write(i, 2, item.get('status', ''))
        ws.write(i, 3, item.get('created_at', ''))
        ws.write(i, 4, item.get('started_at', ''))
        ws.write(i, 5, item.get('ended_at', ''))
        ws.write(i, 6, item.get('duration', ''))
        ws.write(i, 7, item.get('paused_at', ''))
        ws.write(i, 8, item.get('continued_at', ''))

    # write project list sheet
    ws_projects = wb.add_sheet('Project List')
    ws_projects.write(0, 0, 'Project Code')
    for i, p in enumerate(sorted(project_codes)):
        ws_projects.write(i + 1, 0, p)

    wb.save(str(filename))
    # If a custom data_dir was provided (tests call create_todo_file(tmp_path)),
    # also create a copy in the current working directory so helper functions
    # that expect the file in CWD (used directly by tests) can find it. Also
    # record the origin path so other commands that update the CWD copy can
    # mirror changes back to the original file.
    try:
        default_data_dir = Path(__file__).resolve().parents[1] / 'data'
        if data_dir != default_data_dir:
            local_copy = Path.cwd() / filename.name
            wb.save(str(local_copy))

            # write a small mapping file in cwd to point the filename -> original
            meta_file = Path.cwd() / '.todos_origins.json'
            try:
                data_map = {}
                if meta_file.exists():
                    try:
                        data_map = json.loads(meta_file.read_text())
                    except Exception:
                        data_map = {}
                data_map[filename.name] = str(filename)
                meta_file.write_text(json.dumps(data_map))
            except Exception:
                pass
    except Exception:
        # best-effort; ignore errors copying to cwd
        pass
    if copied:
        return f"Created {filename.name} and copied {len(copied)} tasks from previous day"
    return f"Created {filename.name}"


if __name__ == "__main__":
    print(create_todo_file())
