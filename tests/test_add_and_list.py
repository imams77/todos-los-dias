import importlib
import xlrd
from datetime import datetime


def test_add_and_list_roundtrip(tmp_path, monkeypatch):
    # prepare a fresh file
    create_mod = importlib.import_module('commands.create_todo')
    add_mod = importlib.import_module('commands.add_todo')
    list_mod = importlib.import_module('commands.list_todo')

    create_mod.create_todo_file(tmp_path)

    # run add
    res = add_mod.add_todo('TST', 'a task')
    assert 'Added:' in res

    # ensure list prints something (call directly)
    # change cwd to tmp_path so list_todo finds the file
    monkeypatch.chdir(tmp_path)
    # this will print; we just ensure it runs without exception
    list_mod.list_todos('TST')

