from pathlib import Path


def run(data_dir: Path):
    import os
    # import implementation lazily to avoid circular import on package import
    from . import create_todo as _create

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        res = _create.create_todo_file()
        print(res)
        return 0
    finally:
        os.chdir(cwd)
