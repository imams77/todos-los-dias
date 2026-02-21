from pathlib import Path


def run(data_dir: Path, args):
    import os
    if len(args) < 2:
        print("Usage: todo add <CODE> <title>")
        return 1
    code = args[0].upper()
    title = " ".join(args[1:])

    try:
        from . import add_todo as _add
    except Exception:
        try:
            import add_todo as _add
        except Exception:
            print("add command not available (missing implementation)")
            return 1

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        res = _add.add_todo(code, title)
        print(res)
        return 0
    finally:
        os.chdir(cwd)
