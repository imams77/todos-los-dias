from pathlib import Path


def run(data_dir: Path, args):
    import os

    try:
        import summary as _summary
    except Exception:
        try:
            from . import summary as _summary
        except Exception:
            print("summary command not available (missing implementation)")
            return 1

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        if len(args) > 0 and args[0].lower() == 'yesterday':
            from datetime import datetime, timedelta
            d = datetime.now() - timedelta(days=1)
            _summary.print_summary(d)
        else:
            _summary.print_summary()
        return 0
    finally:
        os.chdir(cwd)
