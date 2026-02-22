#!/usr/bin/env python3
"""Argparse-based CLI for the todo manager (commands package).

This provides clearer help and basic validation. It delegates the work to
the per-command wrappers in this package and ensures the `data/` directory
exists (commands/data).
"""
import argparse
import sys
from pathlib import Path

from . import (
    init_cmd,
    add_cmd,
    start_cmd,
    continue_cmd,
    show_cmd,
    list_cmd,
    delete_cmd,
    complete_cmd,
    pause_cmd,
)


def get_data_dir() -> Path:
    # data directory is at the repository root `data/` (not commands/data)
    return Path(__file__).resolve().parent.parent / 'data'


def build_parser() -> argparse.ArgumentParser:
    epilog = (
        "Examples:\n"
        "  todo init\n"
        "  todo add ABC \"Write unit tests\"\n"
        "  todo list\n"
        "  todo list ABC\n"
        "  todo show ABC-001\n"
        "  todo start ABC-001\n"
        "  todo pause ABC-001\n"
        "  todo pause all\n"
        "  todo complete ABC-001\n"
        "  todo delete ABC-001\n\n"
        "Use 'todo <command> --help' for command specific examples."
    )

    parser = argparse.ArgumentParser(
        prog='todo',
        description='Todo manager CLI',
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest='command', title='subcommands')

    sub.add_parser(
        'init',
        help='create today todo file',
        description='Create today todo file.\n\nExample:\n  todo init',
    )

    p = sub.add_parser(
        'add',
        help='add a new todo',
        description='Add a new todo.\n\nExample:\n  todo add ABC "Write unit tests"',
    )
    p.add_argument('code', help='3-letter project code (eg. ABC)')
    p.add_argument('title', nargs='+', help='title of the todo')

    p = sub.add_parser(
        'start',
        help='start a todo',
        description='Start (or continue) a todo.\n\nExample:\n  todo start ABC-001',
    )
    p.add_argument('code', help='todo code (eg. ABC-001)')

    p = sub.add_parser(
        'show',
        help='show a todo',
        description='Show a todo in the verbose format.\n\nExample:\n  todo show ABC-001',
    )
    p.add_argument('code', help='todo code')

    p = sub.add_parser(
        'list',
        help='list todos',
        description='List todos.\n\nExamples:\n  todo list\n  todo list ABC\n  todo list ABC DRAFT',
    )
    p.add_argument('code', nargs='?', help='project code (optional)')
    p.add_argument('status', nargs='*', help='status filter (optional)')

    p = sub.add_parser(
        'delete',
        help='delete a todo',
        description='Delete a todo by code.\n\nExample:\n  todo delete ABC-001',
    )
    p.add_argument('code', help='todo code')

    p = sub.add_parser(
        'complete',
        help='complete a todo',
        description='Mark a todo completed.\n\nExample:\n  todo complete ABC-001',
    )
    p.add_argument('code', help='todo code')

    p = sub.add_parser(
        'pause',
        help='pause a todo or all',
        description='Pause a single todo or all in-progress todos.\n\nExamples:\n  todo pause ABC-001\n  todo pause all',
    )
    p.add_argument('target', help='todo code or "all"')

    p = sub.add_parser(
        'continue',
        help='continue a paused todo',
        description='Continue a paused todo and accumulate duration.\n\nExample:\n  todo continue ABC-001',
    )
    p.add_argument('code', help='todo code (eg. ABC-001)')

    return parser


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()
    args = parser.parse_args(argv)

    data_dir = get_data_dir()
    data_dir.mkdir(exist_ok=True)

    try:
        if args.command == 'init':
            return init_cmd.run(data_dir)

        if args.command == 'add':
            code = args.code.upper()
            title = ' '.join(args.title)
            return add_cmd.run(data_dir, [code, title])

        if args.command == 'start':
            return start_cmd.run(data_dir, [args.code.upper()])

        if args.command == 'continue':
            return continue_cmd.run(data_dir, [args.code.upper()])

        if args.command == 'show':
            return show_cmd.run(data_dir, [args.code.upper()])

        if args.command == 'list':
            if not args.code:
                return list_cmd.run(data_dir, [])
            code = args.code.upper()
            status = ' '.join(args.status).upper() if args.status else None
            if status:
                return list_cmd.run(data_dir, [code, status])
            return list_cmd.run(data_dir, [code])

        if args.command == 'delete':
            return delete_cmd.run(data_dir, [args.code.upper()])

        if args.command == 'complete':
            return complete_cmd.run(data_dir, [args.code.upper()])

        if args.command == 'pause':
            target = args.target.lower()
            if target == 'all':
                return pause_cmd.run(data_dir, ['all'])
            return pause_cmd.run(data_dir, [args.target.upper()])

        parser.print_help()
        return 1

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
