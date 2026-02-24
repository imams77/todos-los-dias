#!/usr/bin/env python3
"""Argparse-based CLI for the todo manager (commands package).

This provides clearer help and basic validation. It delegates the work to
the per-command wrappers in this package and ensures the `data/` directory
exists (commands/data).
"""
import argparse
import sys
from pathlib import Path

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"


class StyledHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format_help(self):
        help_text = super().format_help()
        help_text = help_text.replace('usage:', f'{BOLD}{CYAN}usage:{RESET}')
        help_text = help_text.replace('options:', f'{BOLD}{CYAN}options:{RESET}')
        help_text = help_text.replace('subcommands:', f'{BOLD}{CYAN}subcommands:{RESET}')
        help_text = help_text.replace('Examples:', f'{BOLD}{YELLOW}Examples:{RESET}')
        help_text = help_text.replace('todo ', f'{GREEN}todo {RESET}')
        help_text = help_text.replace('DRAFT', f'{YELLOW}DRAFT{RESET}')
        help_text = help_text.replace('IN PROGRESS', f'{CYAN}IN PROGRESS{RESET}')
        help_text = help_text.replace('COMPLETED', f'{GREEN}COMPLETED{RESET}')
        help_text = help_text.replace('PAUSED', f'{MAGENTA}PAUSED{RESET}')
        return help_text


    # end of StyledHelpFormatter


from . import (
    init_cmd,
    add_cmd,
    start_cmd,
    continue_cmd,
    show_cmd,
    edit_cmd,
    reset_seq_cmd,
    list_cmd,
    delete_cmd,
    complete_cmd,
    pause_cmd,
    summary_cmd,
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
        formatter_class=StyledHelpFormatter,
    )
    sub = parser.add_subparsers(dest='command', title='subcommands')

    sub.add_parser(
        'init',
        help='create today todo file',
        description='Create today todo file.\n\nExample:\n  todo init',
        formatter_class=StyledHelpFormatter,
    )

    p = sub.add_parser(
        'summary',
        help='show summary of todos',
        description='Show summary of todos.\n\nExamples:\n  todo summary\n  todo summary yesterday',
        formatter_class=StyledHelpFormatter,
    )
    p.add_argument('which', nargs='*', help='optional: yesterday')

    p = sub.add_parser(
        'add',
        help='add a new todo',
        description='Add a new todo.\n\nExample:\n  todo add ABC "Write unit tests"',
        formatter_class=StyledHelpFormatter,
    )
    p.add_argument('code', help='3-letter project code (eg. ABC)')
    p.add_argument('title', nargs='+', help='title of the todo')

    p = sub.add_parser(
        'start',
        help='start a todo',
        description='Start (or continue) a todo.\n\nExample:\n  todo start ABC-001',
        formatter_class=StyledHelpFormatter,
    )
    p.add_argument('code', help='todo code (eg. ABC-001)')

    p = sub.add_parser(
        'show',
        help='show a todo',
        description='Show a todo in the verbose format.\n\nExample:\n  todo show ABC-001',
        formatter_class=StyledHelpFormatter,
    )
    p.add_argument('code', help='todo code')

    p = sub.add_parser(
        'edit',
        help='edit a todo',
        description='Edit a todo title interactively.\n\nExample:\n  todo edit ABC-001',
        formatter_class=StyledHelpFormatter,
    )
    p.add_argument('code', help='todo code (eg. ABC-001)')
    p.add_argument('--title', dest='title', help='Set the new title non-interactively')

    p = sub.add_parser(
        'list',
        help='list todos',
        description='List todos.\n\nExamples:\n  todo list\n  todo list ABC\n  todo list ABC --status DRAFT\n  todo list --status PAUSED',
        formatter_class=StyledHelpFormatter,
    )
    p.add_argument('code', nargs='?', help='project code (optional)')
    p.add_argument('--status', dest='status', help='filter by status (DRAFT, IN PROGRESS, PAUSED, COMPLETED)')

    p = sub.add_parser(
        'delete',
        help='delete a todo',
        description='Delete a todo by code.\n\nExample:\n  todo delete ABC-001',
        formatter_class=StyledHelpFormatter,
    )
    p.add_argument('code', help='todo code')

    p = sub.add_parser(
        'complete',
        help='complete a todo',
        description='Mark a todo completed.\n\nExample:\n  todo complete ABC-001',
        formatter_class=StyledHelpFormatter,
    )
    p.add_argument('code', help='todo code')

    p = sub.add_parser(
        'pause',
        help='pause a todo or all',
        description='Pause a single todo or all in-progress todos.\n\nExamples:\n  todo pause ABC-001\n  todo pause all',
        formatter_class=StyledHelpFormatter,
    )
    p.add_argument('target', help='todo code or "all"')

    p = sub.add_parser(
        'continue',
        help='continue a paused todo',
        description='Continue a paused todo and accumulate duration.\n\nExample:\n  todo continue ABC-001',
        formatter_class=StyledHelpFormatter,
    )
    p.add_argument('code', help='todo code (eg. ABC-001)')

    p = sub.add_parser(
        'reset-seq',
        help='reset sequence for a project',
        description='Reset the last used sequence for a project code.\n\nExample:\n  todo reset-seq ABC 42',
        formatter_class=StyledHelpFormatter,
    )
    p.add_argument('code', help='3-letter project code (eg. ABC)')
    p.add_argument('number', help='sequence number to set (integer)')

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

        if args.command == 'edit':
            # pass through optional --title for non-interactive updates
            title_arg = getattr(args, 'title', None)
            if title_arg:
                return edit_cmd.run(data_dir, [args.code.upper(), title_arg])
            return edit_cmd.run(data_dir, [args.code.upper()])

        if args.command == 'list':
            if not args.code and not args.status:
                return list_cmd.run(data_dir, [])
            if args.code and args.status:
                return list_cmd.run(data_dir, [args.code.upper(), args.status.upper()])
            if args.code:
                return list_cmd.run(data_dir, [args.code.upper()])
            return list_cmd.run(data_dir, [args.status.upper()])

        if args.command == 'delete':
            return delete_cmd.run(data_dir, [args.code.upper()])

        if args.command == 'complete':
            return complete_cmd.run(data_dir, [args.code.upper()])

        if args.command == 'pause':
            target = args.target.lower()
            if target == 'all':
                return pause_cmd.run(data_dir, ['all'])
            return pause_cmd.run(data_dir, [args.target.upper()])

        if args.command == 'reset-seq':
            return reset_seq_cmd.run(data_dir, [args.code.upper(), args.number])

        if args.command == 'summary':
            if hasattr(args, 'which') and args.which:
                return summary_cmd.run(data_dir, [args.which[0]])
            return summary_cmd.run(data_dir, [])

        parser.print_help()
        return 1

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
