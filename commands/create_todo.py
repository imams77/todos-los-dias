#!/usr/bin/env python3
from pathlib import Path
import xlwt
from datetime import datetime
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

    ws_projects = wb.add_sheet('Project List')
    ws_projects.write(0, 0, 'Project Code')

    wb.save(str(filename))
    return f"Created {filename.name}"


if __name__ == "__main__":
    print(create_todo_file())
