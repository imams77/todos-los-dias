from pathlib import Path


def run(data_dir: Path, args):
    import os
    if len(args) < 1:
        print("Usage: todo complete <CODE>")
        return 1
    code = args[0].upper()

    try:
        from . import complete_todo as _complete
    except Exception:
        try:
            import complete_todo as _complete
        except Exception:
            print("complete command not available (missing implementation)")
            return 1

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        res = _complete.complete_todo(code)
        print(res)
        return 0
    finally:
        os.chdir(cwd)
