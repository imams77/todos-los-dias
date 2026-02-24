import importlib


def test_status_parsing_variants(tmp_path, monkeypatch):
    # create a fresh todo file and add several items with different statuses
    create_mod = importlib.import_module('commands.create_todo')
    add_mod = importlib.import_module('commands.add_todo')
    list_mod = importlib.import_module('commands.list_todo')

    # prepare file
    create_mod.create_todo_file(tmp_path)
    # add three tasks
    add_mod.add_todo('TST', 'task one')
    add_mod.add_todo('TST', 'task two')
    add_mod.add_todo('TST', 'task three')

    # mark second and third completed using complete_todo
    complete_mod = importlib.import_module('commands.complete_todo')

    monkeypatch.chdir(tmp_path)
    complete_mod.complete_todo('TST-002')
    complete_mod.complete_todo('TST-003')

    # Now exercise list_todos with different status variants
    # direct import of helpers to normalise
    from commands.core.todo_ops import normalize_status

    assert normalize_status('COMPLETED') == 'COMPLETED'
    assert normalize_status('completed') == 'COMPLETED'
    assert normalize_status('complete') == 'COMPLETED'
    assert normalize_status('done') == 'COMPLETED'
    assert normalize_status('in-progress') == 'IN PROGRESS'
    assert normalize_status('in_progress') == 'IN PROGRESS'
    assert normalize_status('In Progress') == 'IN PROGRESS'

    # ensure list_todos accepts the normalized forms via the CLI wrapper
    cli_mod = importlib.import_module('commands.list_cmd')
    # listing by status only should show two completed tasks (no exception means pass)
    res = cli_mod.run(tmp_path, ['COMPLETED'])
    assert res == 0
