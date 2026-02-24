from pathlib import Path
from rich.console import Console

console = Console()


def run(data_dir: Path, args):
    import os, json
    if len(args) < 2:
        console.print("[bold red]Usage:[/bold red] todo reset-seq <CODE> <NUMBER>")
        return 1

    code = args[0].upper()
    try:
        num = int(args[1])
    except Exception:
        console.print("[bold red]Invalid number provided[/bold red]")
        return 1

    # store in repository data dir
    seq_path = Path(__file__).resolve().parents[1] / 'data' / '.todos_seq.json'
    seq_map = {}
    try:
        if seq_path.exists():
            seq_map = json.loads(seq_path.read_text())
    except Exception:
        seq_map = {}

    seq_map[code] = num
    try:
        seq_path.write_text(json.dumps(seq_map))
    except Exception:
        console.print('[bold red]Failed to write sequence file[/bold red]')
        return 1

    console.print(f"[bold green]✓[/bold green] Sequence for {code} set to {num}")
    return 0
