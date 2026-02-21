from pathlib import Path


def run(data_dir: Path, args):
    import os
    if len(args) < 1:
        print("Usage: todo pause <CODE>|all")
        return 1
    target = args[0].lower()

    # try package-local implementations first, fall back to top-level module
    try:
        from . import pause_todo as _pause
    except Exception:
        try:
            import pause_todo as _pause
        except Exception:
            _pause = None

    try:
        from . import pause_all_todo as _pause_all
    except Exception:
        try:
            import pause_all_todo as _pause_all
        except Exception:
            _pause_all = None

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        if target == 'all':
            if _pause_all is None:
                print('pause all command not available')
                return 1
            res = _pause_all.pause_all_todos()
        else:
            if _pause is None:
                print('pause command not available')
                return 1
            res = _pause.pause_todo(args[0].upper())
        print(res)
        return 0
    finally:
        os.chdir(cwd)
