from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner


console = Console()


def run(data_dir: Path, args):
    import os
    if len(args) < 1:
        console.print("[bold red]Usage:[/bold red] todo delete <CODE>")
        return 1
    code = args[0].upper()

    try:
        from . import delete_todo as _del
    except Exception:
        try:
            import delete_todo as _del
        except Exception:
            console.print("[bold red]delete command not available (missing implementation)[/bold red]")
            return 1

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        with Live(Spinner("dots", text="Deleting todo..."), console=console, transient=True) as live:
            res = _del.delete_todo(code)
        if "not found" in res.lower():
            console.print(f"[bold red]✗ {res}[/bold red]")
        else:
            console.print(f"[bold red]🗑 {res}[/bold red]")
        return 0
    finally:
        os.chdir(cwd)
