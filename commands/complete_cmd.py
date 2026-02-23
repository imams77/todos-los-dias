from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner


console = Console()


def run(data_dir: Path, args):
    import os
    if len(args) < 1:
        console.print("[bold red]Usage:[/bold red] todo complete <CODE>")
        return 1
    code = args[0].upper()

    try:
        from . import complete_todo as _complete
    except Exception:
        try:
            import complete_todo as _complete
        except Exception:
            console.print("[bold red]complete command not available (missing implementation)[/bold red]")
            return 1

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        with Live(Spinner("dots", text="Completing todo..."), console=console, transient=True) as live:
            res = _complete.complete_todo(code)
        if "not found" in res.lower():
            console.print(f"[bold red]✗ {res}[/bold red]")
        else:
            console.print(f"[bold green]✓ {res}[/bold green]")
        return 0
    finally:
        os.chdir(cwd)
