from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table


console = Console()


def run(data_dir: Path, args):
    import os
    if len(args) < 1:
        console.print("[bold red]Usage:[/bold red] todo show <CODE>")
        return 1
    code = args[0].upper()

    try:
        from . import show_todo as _show
    except Exception:
        try:
            import show_todo as _show
        except Exception:
            console.print("[bold red]show command not available (missing implementation)[/bold red]")
            return 1

    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        res = _show.show_todo(code)
        
        if res == "not exist":
            console.print(f"[bold red]✗ Todo {code} not found[/bold red]")
            return 1
        
        if "not found" in res.lower():
            console.print(f"[bold red]✗ {res}[/bold red]")
            return 1
        
        lines = res.split('\n')
        code_line = lines[0]
        
        table = Table(box=None, show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        for line in lines[1:]:
            if ':' in line:
                key, val = line.split(':', 1)
                table.add_row(key.strip(), val.strip())
        
        console.print(Panel(table, title=f"[bold cyan]{code_line}[/bold cyan]", border_style="cyan"))
        return 0
    finally:
        os.chdir(cwd)
