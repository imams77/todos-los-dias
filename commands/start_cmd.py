from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner


console = Console()


def run(data_dir: Path, args):
    import os
    if len(args) < 1:
        console.print("[bold red]Usage:[/bold red] todo start <CODE>")
        return 1
    code = args[0].upper()

    try:
        from . import start_todo as _start
    except Exception:
        try:
            import start_todo as _start
        except Exception:
            console.print("[bold red]start command not available (missing implementation)[/bold red]")
            return 1

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        with Live(Spinner("dots", text="Starting todo..."), console=console, transient=True) as live:
            res = _start.start_todo(code)
        if "not found" in res.lower() or "not found" in res.lower():
            console.print(f"[bold red]✗ {res}[/bold red]")
        elif "continued" in res.lower():
            console.print(f"[bold yellow]▶ {res}[/bold yellow]")
        else:
            console.print(f"[bold green]▶ {res}[/bold green]")
        return 0
    finally:
        os.chdir(cwd)
