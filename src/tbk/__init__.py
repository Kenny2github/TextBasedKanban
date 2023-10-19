import argparse
import os
import sys

__all__ = [
    'main',
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
    if not _find_tbk_dir():
        sys.exit('fatal: no .tbk directory found in working directory or any parent')

    parser = argparse.ArgumentParser(
        description='Vaguely git-flavored text-based Kanban board management.')

    args = parser.parse_args(cmdargs)

    print(args)
