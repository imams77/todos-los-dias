#!/usr/bin/env python3
import xlrd
from datetime import datetime
import os


def list_todos(code=None, status=None):
    today = datetime.now()
    filename = f"todos-{today.strftime('%d-%m-%Y')}.xls"
    if not os.path.exists(filename):
        print("Todo file for today not found. Run 'init for today' first.")
        return

    wb = xlrd.open_workbook(filename)
    ws = wb.sheet_by_name('Todos')

    for row in range(1, ws.nrows):
        row_code = ws.cell_value(row, 0)
        if code:
            # allow project code (ABC) or full code (ABC-001)
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
        created = ws.cell_value(row, 3) if ws.ncols > 3 else ''
        started = ws.cell_value(row, 4) if ws.ncols > 4 else ''
        ended = ws.cell_value(row, 5) if ws.ncols > 5 else ''
        duration = ws.cell_value(row, 6) if ws.ncols > 6 else ''

        print(f"{row_code}, {title}, {st}, {created}, {started}, {ended}, {duration}")


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        list_todos()
    elif len(sys.argv) == 2:
        list_todos(sys.argv[1])
    else:
        list_todos(sys.argv[1], ' '.join(sys.argv[2:]))
