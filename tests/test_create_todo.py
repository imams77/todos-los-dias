import importlib
import xlrd
from datetime import datetime


def test_create_file_creates_file_and_sheets(tmp_path):
    create_mod = importlib.import_module('commands.create_todo')
    # create in tmp path
    res = create_mod.create_todo_file(tmp_path)
    fname = tmp_path / f"todos-{datetime.now().strftime('%d-%m-%Y')}.xls"
    assert fname.exists()
    wb = xlrd.open_workbook(str(fname))
    names = wb.sheet_names()
    assert 'Todos' in names
    assert 'Project List' in names


def test_create_file_already_exists_returns_message(tmp_path):
    create_mod = importlib.import_module('commands.create_todo')
    create_mod.create_todo_file(tmp_path)
    res2 = create_mod.create_todo_file(tmp_path)
    assert 'file for today already exists' in res2
