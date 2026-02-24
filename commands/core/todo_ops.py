#!/usr/bin/env python3
"""Shared helpers for manipulating the Todos xls file.

This centralises the small but repetitive workbook read/modify/write logic
used by the start/continue implementations.
"""
import xlrd
import re
import xlwt
from datetime import datetime


HEADERS = ['code', 'title', 'status', 'created at', 'started at', 'ended at', 'duration', 'paused at', 'continued at']


def _parse_dt(s: str):
    try:
        return datetime.strptime(s, '%d/%m/%Y %H:%M:%S')
    except Exception:
        return None


def find_row_by_code(filename: str, code: str):
    """Return the (wb, ws, row_index) for the given code or (wb, ws, None)."""
    wb = xlrd.open_workbook(filename)
    ws = wb.sheet_by_name('Todos')
    row_to_update = None
    for row in range(1, ws.nrows):
        if ws.cell_value(row, 0) == code:
            row_to_update = row
            break
    return wb, ws, row_to_update


def safe_float(val):
    """Safely parse a cell value that represents an accumulated duration.

    Historically durations were stored as numeric seconds. New files store
    durations as "HH:MM:SS" strings. This helper understands both formats
    and always returns total seconds as a float.
    """
    try:
        if val in (None, ''):
            return 0.0
        # numeric cell (xlrd may return float/int)
        if isinstance(val, (int, float)):
            return float(val)
        # string: accept HH:MM:SS, MM:SS or a plain numeric string
        if isinstance(val, str):
            s = val.strip()
            if ':' in s:
                parts = s.split(':')
                try:
                    parts = [int(p) for p in parts]
                except Exception:
                    return 0.0
                if len(parts) == 3:
                    h, m, sec = parts
                    return float(h * 3600 + m * 60 + sec)
                if len(parts) == 2:
                    m, sec = parts
                    return float(m * 60 + sec)
                # unexpected format, fall through
            # plain numeric string
            try:
                return float(s)
            except Exception:
                return 0.0
        return 0.0
    except Exception:
        return 0.0


def format_seconds_as_hms(seconds: float) -> str:
    """Format seconds as HH:MM:SS (zero-padded).

    Hours are zero-padded to at least two digits. Rounds to the nearest
    second.
    """
    try:
        total = int(round(float(seconds)))
    except Exception:
        total = 0
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def normalize_status(s):
    """Normalize a status-like string to one of the canonical values.

    Recognises common variants such as "in-progress", "IN_PROGRESS",
    "in progress", "inprogress" and maps them to the canonical
    uppercase values used in the XLS file: 'DRAFT', 'IN PROGRESS',
    'PAUSED', 'COMPLETED'. Returns None for unknown inputs.
    """
    if s is None:
        return None
    try:
        ss = str(s).strip().lower()
    except Exception:
        return None

    # collapse separators (spaces, hyphens, underscores) to a compact key
    key = re.sub(r"[\s\-_]+", "", ss)

    mapping = {
        'draft': 'DRAFT',
        'inprogress': 'IN PROGRESS',
        'paused': 'PAUSED',
        'completed': 'COMPLETED',
        'complete': 'COMPLETED',
        'done': 'COMPLETED',
    }

    return mapping.get(key)


def write_updated_file(filename: str, row_to_update: int, updates: dict, today: datetime):
    """Write a new workbook copying the existing file and applying updates.

    - filename: path to existing xls file
    - row_to_update: 1-based row index to change (None to just copy)
    - updates: mapping of column_index -> value to set for the target row
    - today: datetime used to format any timestamps
    """
    wb_src = xlrd.open_workbook(filename)
    ws_src = wb_src.sheet_by_name('Todos')

    wb_write = xlwt.Workbook()
    ws_write = wb_write.add_sheet('Todos')
    ws_projects_write = wb_write.add_sheet('Project List')

    for i, h in enumerate(HEADERS):
        ws_write.write(0, i, h)

    # copy rows and apply updates for the target row
    for row in range(1, ws_src.nrows):
        for col in range(ws_src.ncols):
            val = ws_src.cell_value(row, col)
            if row == row_to_update and col in updates:
                val = updates[col]
            ws_write.write(row, col, val)

        # if the original had fewer than 9 columns, ensure schema columns exist
        if row == row_to_update and ws_src.ncols < len(HEADERS):
            for col in range(ws_src.ncols, len(HEADERS)):
                if col in updates:
                    ws_write.write(row, col, updates[col])
                else:
                    ws_write.write(row, col, '')

    # copy project list if present
    try:
        if 'Project List' in wb_src.sheet_names():
            ws_proj = wb_src.sheet_by_name('Project List')
            ws_projects_write.write(0, 0, 'Project Code')
            for r in range(1, ws_proj.nrows):
                ws_projects_write.write(r, 0, ws_proj.cell_value(r, 0))
        else:
            ws_projects_write.write(0, 0, 'Project Code')
    except Exception:
        ws_projects_write.write(0, 0, 'Project Code')

    wb_write.save(filename)
