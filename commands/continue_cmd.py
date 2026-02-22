from pathlib import Path


def run(data_dir: Path, args):
    import os
    if len(args) < 1:
        print("Usage: todo continue <CODE>")
        return 1
    code = args[0].upper()

    try:
        from . import continue_todo as _cont
    except Exception:
        try:
            import continue_todo as _cont
        except Exception:
            print("continue command not available (missing implementation)")
            return 1

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        res = _cont.continue_todo(code)
        print(res)
        return 0
    finally:
        os.chdir(cwd)
