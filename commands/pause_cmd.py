from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner


console = Console()


def run(data_dir: Path, args):
    import os
    if len(args) < 1:
        console.print("[bold red]Usage:[/bold red] todo pause <CODE>|all")
        return 1
    target = args[0].lower()

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
                console.print("[bold red]pause all command not available[/bold red]")
                return 1
            with Live(Spinner("dots", text="Pausing all todos..."), console=console, transient=True) as live:
                res = _pause_all.pause_all_todos()
            console.print(f"[bold yellow]⏸ {res}[/bold yellow]")
        else:
            if _pause is None:
                console.print("[bold red]pause command not available[/bold red]")
                return 1
            with Live(Spinner("dots", text="Pausing todo..."), console=console, transient=True) as live:
                res = _pause.pause_todo(args[0].upper())
            if "not found" in res.lower():
                console.print(f"[bold red]✗ {res}[/bold red]")
            else:
                console.print(f"[bold yellow]⏸ {res}[/bold yellow]")
        return 0
    finally:
        os.chdir(cwd)
