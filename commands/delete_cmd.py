from pathlib import Path


def run(data_dir: Path, args):
    import os
    if len(args) < 1:
        print("Usage: todo delete <CODE>")
        return 1
    code = args[0].upper()

    try:
        from . import delete_todo as _del
    except Exception:
        try:
            import delete_todo as _del
        except Exception:
            print("delete command not available (missing implementation)")
            return 1

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        res = _del.delete_todo(code)
        print(res)
        return 0
    finally:
        os.chdir(cwd)
