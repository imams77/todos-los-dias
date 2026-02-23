from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner


console = Console()


def run(data_dir: Path, args):
    import os
    if len(args) < 1:
        console.print("[bold red]Usage:[/bold red] todo continue <CODE>|all")
        return 1
    target = args[0].lower()

    try:
        from . import continue_todo as _cont
    except Exception:
        try:
            import continue_todo as _cont
        except Exception:
            _cont = None

    try:
        from . import continue_all_todo as _cont_all
    except Exception:
        try:
            import continue_all_todo as _cont_all
        except Exception:
            _cont_all = None

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        if target == 'all':
            if _cont_all is None:
                console.print("[bold red]continue all command not available[/bold red]")
                return 1
            with Live(Spinner("dots", text="Continuing all todos..."), console=console, transient=True) as live:
                res = _cont_all.continue_all_todos()
            console.print(f"[bold green]▶ {res}[/bold green]")
        else:
            if _cont is None:
                console.print("[bold red]continue command not available[/bold red]")
                return 1
            code = args[0].upper()
            with Live(Spinner("dots", text="Continuing todo..."), console=console, transient=True) as live:
                res = _cont.continue_todo(code)
            if "not found" in res.lower():
                console.print(f"[bold red]✗ {res}[/bold red]")
            else:
                console.print(f"[bold green]▶ {res}[/bold green]")
        return 0
    finally:
        os.chdir(cwd)
