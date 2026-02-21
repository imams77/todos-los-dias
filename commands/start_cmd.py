from pathlib import Path


def run(data_dir: Path, args):
    import os
    if len(args) < 1:
        print("Usage: todo start <CODE>")
        return 1
    code = args[0].upper()

    try:
        from . import start_todo as _start
    except Exception:
        try:
            import start_todo as _start
        except Exception:
            print("start command not available (missing implementation)")
            return 1

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        res = _start.start_todo(code)
        print(res)
        return 0
    finally:
        os.chdir(cwd)
