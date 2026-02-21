from pathlib import Path


def run(data_dir: Path, args):
    import os
    if len(args) < 1:
        print("Usage: todo show <CODE>")
        return 1
    code = args[0].upper()

    # lazy import the implementation so CLI can load even if some
    # implementations are missing during incremental work
    try:
        from . import show_todo as _show
    except Exception:
        try:
            import show_todo as _show
        except Exception:
            print("show command not available (missing implementation)")
            return 1

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        res = _show.show_todo(code)
        print(res)
        return 0
    finally:
        os.chdir(cwd)
