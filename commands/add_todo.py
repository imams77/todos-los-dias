#!/usr/bin/env python3
import xlwt
import xlrd
from datetime import datetime
import os
import sys

def add_todo(code, title):
    today = datetime.now()
    filename = f"todos-{today.strftime('%d-%m-%Y')}.xls"
    
    if not os.path.exists(filename):
        return f"Todo file for today not found. Run 'init for today' first."
    
    wb = xlrd.open_workbook(filename)
    
    existing_codes = []
    for sheet in wb.sheets():
        if sheet.name == 'Todos':
            for row in range(1, sheet.nrows):
                existing_codes.append(sheet.cell_value(row, 0))
    
    seq_nums = [int(c.split('-')[1]) for c in existing_codes if c.startswith(code + '-')]
    next_num = max(seq_nums) + 1 if seq_nums else 1
    new_code = f"{code}-{next_num:03d}"
    
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
    return f"Added: {new_code} - {title}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: add_todo.py <CODE> <title>")
        sys.exit(1)
    print(add_todo(sys.argv[1], sys.argv[2]))
