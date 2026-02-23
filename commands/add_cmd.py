from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner


console = Console()


def run(data_dir: Path, args):
    import os
    if len(args) < 2:
        console.print("[bold red]Usage:[/bold red] todo add <CODE> <title>")
        return 1
    code = args[0].upper()
    title = " ".join(args[1:])

    try:
        from . import add_todo as _add
    except Exception:
        try:
            import add_todo as _add
        except Exception:
            console.print("[bold red]add command not available (missing implementation)[/bold red]")
            return 1

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        with Live(Spinner("dots", text="Adding todo..."), console=console, transient=True) as live:
            res = _add.add_todo(code, title)
        console.print(f"[bold green]✓[/bold green] {res}")
        return 0
    finally:
        os.chdir(cwd)
