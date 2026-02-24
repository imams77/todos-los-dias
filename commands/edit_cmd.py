from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

console = Console()


def run(data_dir: Path, args):
    import os
    if len(args) < 1:
        console.print("[bold red]Usage:[/bold red] todo edit <CODE>")
        return 1
    code = args[0].upper()

    try:
        from . import show_todo as _show
    except Exception:
        try:
            import show_todo as _show
        except Exception:
            console.print("[bold red]show command not available (needed to fetch current values)[/bold red]")
            return 1

    try:
        from . import add_todo as _add
    except Exception:
        try:
            import add_todo as _add
        except Exception:
            _add = None

    # load current todo
    cwd = os.getcwd()
    try:
        os.chdir(str(data_dir))
        res = _show.show_todo(code)
        if res == 'not exist':
            console.print(f"[bold red]✗ Todo {code} not found[/bold red]")
            return 1

        # parse the show output to get current title
        title = ''
        for line in res.splitlines()[1:]:
            if line.startswith('title:'):
                title = line.split(':', 1)[1].strip()
                break

        # If --title was provided use it (non-interactive mode)
        new_title = None
        if len(args) > 1 and args[1]:
            new_title = args[1]
        else:
            # prompt the user with current title as default
            try:
                new_title = Prompt.ask(f"Title", default=title)
            except EOFError:
                console.print("[bold red]No input provided. Aborting.[/bold red]")
                return 1

        # perform edit: open file and rewrite the Todos sheet with updated title
        import xlrd, xlwt
        from datetime import datetime

        today = datetime.now()
        filename = f"todos-{today.strftime('%d-%m-%Y')}.xls"
        # support mapping to origin file when tests created the file in tmp dir
        try:
            import json
            from pathlib import Path as P
            meta = P.cwd() / '.todos_origins.json'
            if meta.exists():
                try:
                    m = json.loads(meta.read_text())
                    if filename in m:
                        filename = m[filename]
                except Exception:
                    pass
        except Exception:
            pass

        if not os.path.exists(filename):
            console.print("[bold red]Todo file for today not found. Run 'init for today' first.[/bold red]")
            return 1

        wb = xlrd.open_workbook(filename)
        ws = wb.sheet_by_name('Todos')

        row_to_update = None
        for row in range(1, ws.nrows):
            if ws.cell_value(row, 0) == code:
                row_to_update = row
                break

        if row_to_update is None:
            console.print(f"[bold red]✗ Todo {code} not found[/bold red]")
            return 1

        # create new workbook and copy rows, replacing title cell for target row
        wb_write = xlwt.Workbook()
        ws_write = wb_write.add_sheet('Todos')
        ws_projects_write = wb_write.add_sheet('Project List')

        headers = ['code', 'title', 'status', 'created at', 'started at', 'ended at', 'duration', 'paused at', 'continued at']
        for i, h in enumerate(headers):
            ws_write.write(0, i, h)

        for row in range(1, ws.nrows):
            for col in range(ws.ncols):
                val = ws.cell_value(row, col)
                if row == row_to_update and col == 1:
                    val = new_title
                ws_write.write(row, col, val)

        # ensure remaining header columns exist for the updated row
        if ws.ncols < len(headers):
            for row in range(1, ws.nrows):
                if row == row_to_update:
                    for col in range(ws.ncols, len(headers)):
                        ws_write.write(row, col, '')

        # copy project list if present
        try:
            if 'Project List' in wb.sheet_names():
                ws_proj = wb.sheet_by_name('Project List')
                ws_projects_write.write(0, 0, 'Project Code')
                for r in range(1, ws_proj.nrows):
                    ws_projects_write.write(r, 0, ws_proj.cell_value(r, 0))
            else:
                ws_projects_write.write(0, 0, 'Project Code')
        except Exception:
            ws_projects_write.write(0, 0, 'Project Code')

        wb_write.save(filename)
        console.print(f"[bold green]✓[/bold green] Updated title for {code}")
        return 0
    finally:
        os.chdir(cwd)
