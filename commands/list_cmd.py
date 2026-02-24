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

        # If a single argument is provided, it may be either a project code
        # (eg. ABC) or a status filter (eg. PAUSED). Detect status keywords
        # and call the underlying list_todos accordingly.
        if len(args) == 1:
            single = args[0]
            # use normalize_status if available from shared helpers
            try:
                from .core.todo_ops import normalize_status
            except Exception:
                try:
                    from commands.core.todo_ops import normalize_status
                except Exception:
                    normalize_status = None

            norm = normalize_status(single) if normalize_status else None
            if norm:
                # treat as status filter (no project code)
                _list.list_todos(None, norm)
                return 0

            # otherwise treat as project code
            code = single.upper()
            _list.list_todos(code)
            return 0

        # multiple args: first is project code, remainder form the status
        code = args[0].upper()
        status = " ".join(args[1:])
        _list.list_todos(code, status)
        return 0
    finally:
        os.chdir(cwd)
