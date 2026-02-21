#!/usr/bin/env python3
import xlrd
import xlwt
from datetime import datetime
import os


def delete_todo(code):
    today = datetime.now()
    filename = f"todos-{today.strftime('%d-%m-%Y')}.xls"
    if not os.path.exists(filename):
        return f"Todo file for today not found. Run 'init for today' first."

    wb = xlrd.open_workbook(filename)
    ws = wb.sheet_by_name('Todos')

    row_to_delete = None
    for row in range(1, ws.nrows):
        if ws.cell_value(row, 0) == code:
            row_to_delete = row
            break

    if row_to_delete is None:
        return f"Todo {code} not found"

    # collect remaining project codes while copying rows
    remaining_projects = set()

    wb_write = xlwt.Workbook()
    ws_write = wb_write.add_sheet('Todos')
    ws_projects_write = wb_write.add_sheet('Project List')

    headers = ['code', 'title', 'status', 'created at', 'started at', 'ended at', 'duration', 'paused at', 'continued at']
    for i, h in enumerate(headers):
        ws_write.write(0, i, h)

    new_row = 1
    for row in range(1, ws.nrows):
        if row == row_to_delete:
            continue
        # write up to 9 columns to keep schema consistent
        for col in range(0, 9):
            val = ws.cell_value(row, col) if col < ws.ncols else ''
            ws_write.write(new_row, col, val)

        # record project code
        code_val = ws.cell_value(row, 0) if ws.ncols > 0 else ''
        if code_val:
            try:
                proj = code_val.split('-')[0]
                if proj:
                    remaining_projects.add(proj)
            except Exception:
                pass

        new_row += 1

    # write project list (reconstructed)
    ws_projects_write.write(0, 0, 'Project Code')
    for i, p in enumerate(sorted(remaining_projects)):
        ws_projects_write.write(i + 1, 0, p)

    wb_write.save(filename)
    return f"Deleted: {code}"


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: delete_todo.py <CODE>')
    else:
        print(delete_todo(sys.argv[1]))
