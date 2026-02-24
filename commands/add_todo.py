#!/usr/bin/env python3
import xlwt
import xlrd
from datetime import datetime
import os
import sys
import json
from pathlib import Path


def _read_seq_map(seq_path: Path):
    try:
        if seq_path.exists():
            return json.loads(seq_path.read_text())
    except Exception:
        return {}
    return {}


def _write_seq_map(seq_path: Path, seq_map: dict):
    try:
        seq_path.write_text(json.dumps(seq_map))
    except Exception:
        # best-effort; ignore
        pass


def add_todo(code, title):
    # normalize project code
    code = str(code).upper()

    today = datetime.now()
    filename = f"todos-{today.strftime('%d-%m-%Y')}.xls"

    if not os.path.exists(filename):
        return f"Todo file for today not found. Run 'init for today' first."

    # persistent seq store in the repository data/ directory
    default_data_dir = Path(__file__).resolve().parents[1] / 'data'
    default_data_dir.mkdir(parents=True, exist_ok=True)
    seq_store_name = '.todos_seq.json'
    seq_path = default_data_dir / seq_store_name
    seq_map = _read_seq_map(seq_path)

    # find the maximum existing sequence for this code across all todo files
    import glob
    max_seq_found = 0
    for fpath in glob.glob('todos-*.xls'):
        try:
            wb_other = xlrd.open_workbook(fpath)
            if 'Todos' not in wb_other.sheet_names():
                continue
            ws_other = wb_other.sheet_by_name('Todos')
            for row in range(1, ws_other.nrows):
                try:
                    val = ws_other.cell_value(row, 0)
                    if isinstance(val, str) and val.startswith(code + '-') and '-' in val:
                        parts = val.split('-')
                        num = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
                        if num > max_seq_found:
                            max_seq_found = num
                except Exception:
                    continue
        except Exception:
            continue

    last_used = int(seq_map.get(code, 0) or 0)
    last_used = max(last_used, max_seq_found)
    next_num = last_used + 1
    new_code = f"{code}-{next_num:03d}"

    # open today's workbook and collect existing codes for project list
    wb = xlrd.open_workbook(filename)
    existing_codes = []
    for sheet in wb.sheets():
        if sheet.name == 'Todos':
            for row in range(1, sheet.nrows):
                existing_codes.append(sheet.cell_value(row, 0))

    ws_todos = wb.sheet_by_name('Todos')
    next_row = ws_todos.nrows

    ws = xlwt.Workbook()
    ws_todos_write = ws.add_sheet('Todos')
    ws_projects_write = ws.add_sheet('Project List')

    headers = ['code', 'title', 'status', 'created at', 'started at', 'ended at', 'duration', 'paused at', 'continued at']
    for i, h in enumerate(headers):
        ws_todos_write.write(0, i, h)

    for row in range(1, ws_todos.nrows):
        for col in range(ws_todos.ncols):
            val = ws_todos.cell_value(row, col)
            ws_todos_write.write(row, col, val)

    ws_todos_write.write(next_row, 0, new_code)
    ws_todos_write.write(next_row, 1, title)
    ws_todos_write.write(next_row, 2, 'DRAFT')
    ws_todos_write.write(next_row, 3, today.strftime('%d/%m/%Y %H:%M:%S'))

    ws_projects_write.write(0, 0, 'Project Code')
    projects = list(set([c.split('-')[0] for c in existing_codes] + [code]))
    for i, p in enumerate(sorted(projects)):
        ws_projects_write.write(i + 1, 0, p)

    ws.save(filename)

    # update seq map and persist it next to the data file (cwd)
    try:
        seq_map[code] = next_num
        _write_seq_map(seq_path, seq_map)
    except Exception:
        # best-effort only
        pass

    # If there is a mapping file created by create_todo_file that points the
    # filename -> original data_dir path, also save the workbook to that
    # original location so callers that created the file in a custom data
    # directory (tests) see the updates there as well.
    try:
        meta_file = Path.cwd() / '.todos_origins.json'
        if meta_file.exists():
            try:
                data_map = json.loads(meta_file.read_text())
                orig = data_map.get(Path(filename).name)
                if orig:
                    ws.save(str(Path(orig)))
            except Exception:
                pass
    except Exception:
        pass

    return f"Added: {new_code} - {title}"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: add_todo.py <CODE> <title>")
        sys.exit(1)
    print(add_todo(sys.argv[1], sys.argv[2]))
