#!/usr/bin/env python3
from pathlib import Path
import xlwt
import xlrd
from datetime import datetime, timedelta
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

    if prev_filename.exists():
        try:
            prev_wb = xlrd.open_workbook(str(prev_filename))
            if 'Todos' in prev_wb.sheet_names():
                prev_ws = prev_wb.sheet_by_name('Todos')
                for row in range(1, prev_ws.nrows):
                    prev_code = prev_ws.cell_value(row, 0) if prev_ws.ncols > 0 else ''
                    prev_title = prev_ws.cell_value(row, 1) if prev_ws.ncols > 1 else ''
                    prev_status = prev_ws.cell_value(row, 2) if prev_ws.ncols > 2 else ''
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
                        copied.append((new_code, prev_title))
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

    # write copied tasks into today's Todos sheet
    for i, (code, title) in enumerate(copied, start=1):
        ws.write(i, 0, code)
        ws.write(i, 1, title)
        ws.write(i, 2, 'DRAFT')
        ws.write(i, 3, today.strftime('%d/%m/%Y %H:%M:%S'))

    # write project list sheet
    ws_projects = wb.add_sheet('Project List')
    ws_projects.write(0, 0, 'Project Code')
    for i, p in enumerate(sorted(project_codes)):
        ws_projects.write(i + 1, 0, p)

    wb.save(str(filename))
    if copied:
        return f"Created {filename.name} and copied {len(copied)} tasks from previous day"
    return f"Created {filename.name}"


if __name__ == "__main__":
    print(create_todo_file())
