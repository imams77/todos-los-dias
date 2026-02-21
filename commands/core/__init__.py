"""Core implementations for todo manager commands.

Each function accepts an optional `data_dir` parameter (Path or str). If not
provided, the default data directory is `<repo-root>/data`.
"""

from pathlib import Path

def default_data_dir():
    # two parents up from this file -> repo root
    return Path(__file__).resolve().parents[2] / 'data'
