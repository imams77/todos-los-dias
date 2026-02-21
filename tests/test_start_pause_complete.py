import importlib
from datetime import datetime


def test_start_pause_complete_flow(tmp_path, monkeypatch):
    create_mod = importlib.import_module('commands.create_todo')
    add_mod = importlib.import_module('commands.add_todo')
    start_mod = importlib.import_module('commands.start_todo')
    pause_mod = importlib.import_module('commands.pause_todo')
    complete_mod = importlib.import_module('commands.complete_todo')

    create_mod.create_todo_file(tmp_path)
    # add an item
    res = add_mod.add_todo('XYZ', 'flow task')
    assert 'Added:' in res

    monkeypatch.chdir(tmp_path)
    # start
    r1 = start_mod.start_todo('XYZ-001')
    assert 'Started' in r1 or 'Continued' in r1

    # pause
    r2 = pause_mod.pause_todo('XYZ-001')
    assert 'Paused' in r2

    # complete
    r3 = complete_mod.complete_todo('XYZ-001')
    assert 'Completed' in r3
