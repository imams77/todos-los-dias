#!/usr/bin/env python3
import xlwt
import xlrd
from datetime import datetime
import sys
import os

def start_todo(code):
    today = datetime.now()
    filename = f"todos-{today.strftime('%d-%m-%Y')}.xls"
    
    if not os.path.exists(filename):
        return f"Todo file for today not found. Run 'init for today' first."
    
    wb = xlrd.open_workbook(filename)
    ws = wb.sheet_by_name('Todos')
    
    row_to_update = None
    for row in range(1, ws.nrows):
        if ws.cell_value(row, 0) == code:
            row_to_update = row
            break
    
    if row_to_update is None:
        return f"Todo {code} not found"
    
    current_status = ws.cell_value(row_to_update, 2) if ws.ncols > 2 else ''
    
    if current_status == 'PAUSED':
        paused_at = ws.cell_value(row_to_update, 7)
        if not paused_at:
            return f"Todo {code} has no paused at timestamp"
        
        paused_dt = datetime.strptime(paused_at, '%d/%m/%Y %H:%M:%S')
        added_seconds = (today - paused_dt).total_seconds()
        
        existing_duration = 0.0
        if ws.ncols > 6:
            duration_val = ws.cell_value(row_to_update, 6)
            if duration_val:
                try:
                    existing_duration = float(duration_val)
                except (ValueError, TypeError):
                    pass
        
        total_duration = existing_duration + added_seconds
        
        wb_write = xlwt.Workbook()
        ws_write = wb_write.add_sheet('Todos')
        ws_projects_write = wb_write.add_sheet('Project List')
        
        headers = ['code', 'title', 'status', 'created at', 'started at', 'ended at', 'duration', 'paused at', 'continued at']
        for i, h in enumerate(headers):
            ws_write.write(0, i, h)
        
        for row in range(1, ws.nrows):
            for col in range(ws.ncols):
                val = ws.cell_value(row, col)
                if row == row_to_update and col == 2:
                    val = 'IN PROGRESS'
                elif row == row_to_update and col == 6:
                    val = total_duration
                elif row == row_to_update and col == 7:
                    val = ''
                elif row == row_to_update and col == 8:
                    val = today.strftime('%d/%m/%Y %H:%M:%S')
                ws_write.write(row, col, val)
            
            if row == row_to_update and ws.ncols < 9:
                for col in range(ws.ncols, 9):
                    if col == 6:
                        ws_write.write(row, col, total_duration)
                    elif col == 8:
                        ws_write.write(row, col, today.strftime('%d/%m/%Y %H:%M:%S'))
        
        wb_projects = xlrd.open_workbook(filename)
        ws_projects = wb_projects.sheet_by_name('Project List')
        ws_projects_write.write(0, 0, 'Project Code')
        for row in range(1, ws_projects.nrows):
            ws_projects_write.write(row, 0, ws_projects.cell_value(row, 0))
        
        wb_write.save(filename)
        return f"Continued: {code}"
    
    wb_write = xlwt.Workbook()
    ws_write = wb_write.add_sheet('Todos')
    ws_projects_write = wb_write.add_sheet('Project List')
    
    headers = ['code', 'title', 'status', 'created at', 'started at', 'ended at', 'duration', 'paused at', 'continued at']
    for i, h in enumerate(headers):
        ws_write.write(0, i, h)
    
    for row in range(1, ws.nrows):
        for col in range(ws.ncols):
            val = ws.cell_value(row, col)
            if row == row_to_update and col == 2:
                val = 'IN PROGRESS'
            elif row == row_to_update and col == 4:
                val = today.strftime('%d/%m/%Y %H:%M:%S')
            ws_write.write(row, col, val)
    
    wb_projects = xlrd.open_workbook(filename)
    ws_projects = wb_projects.sheet_by_name('Project List')
    ws_projects_write.write(0, 0, 'Project Code')
    for row in range(1, ws_projects.nrows):
        ws_projects_write.write(row, 0, ws_projects.cell_value(row, 0))
    
    wb_write.save(filename)
    return f"Started: {code}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: start_todo.py <CODE>")
        sys.exit(1)
    print(start_todo(sys.argv[1]))
