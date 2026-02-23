from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner


console = Console()


def run(data_dir: Path):
    import os
    from . import create_todo as _create

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        with Live(Spinner("dots", text="Initializing..."), console=console, transient=True) as live:
            res = _create.create_todo_file()
        if "already exists" in res.lower():
            console.print(f"[bold yellow]✓ {res}[/bold yellow]")
        else:
            console.print(f"[bold green]✓ {res}[/bold green]")
        return 0
    finally:
        os.chdir(cwd)
