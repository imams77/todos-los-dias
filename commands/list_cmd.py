from pathlib import Path


def run(data_dir: Path, args):
    import os

    # lazy import implementation
    try:
        import list_todo as _list
    except Exception:
        try:
            from . import list_todo as _list
        except Exception:
            print("list command not available (missing implementation)")
            return 1

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        if len(args) == 0:
            _list.list_todos()
            return 0
        if len(args) == 1:
            code = args[0].upper()
            _list.list_todos(code)
            return 0
        code = args[0].upper()
        status = " ".join(args[1:]).upper()
        _list.list_todos(code, status)
        return 0
    finally:
        os.chdir(cwd)
