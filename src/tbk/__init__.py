import argparse
import os
import sys

from .cmd.init import setup as setup_init
from .cmd.show import setup as setup_show
from .cmd.status import setup as setup_status

__all__ = [
    'main',
]

_NO_NEED_TBK_DIR = [
    'init',
]

def _find_tbk_dir() -> bool:
    last_dir = os.getcwd()
    while '.tbk' not in os.listdir():
        os.chdir('..')
        if os.getcwd() == last_dir:
            return False
        last_dir = os.getcwd()
    return True

def main(cmdargs: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description='Vaguely git-flavored text-based Kanban board management.')

    subparsers = parser.add_subparsers(required=True, dest='cmd')

    setup_init(subparsers)
    setup_show(subparsers)
    setup_status(subparsers)

    args = parser.parse_args(cmdargs)

    if args.cmd not in _NO_NEED_TBK_DIR and not _find_tbk_dir():
        sys.exit('fatal: no .tbk directory found in working directory or any parent')

    args.func(args)
