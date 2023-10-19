from __future__ import annotations
from argparse import _SubParsersAction, ArgumentParser
import os
from .consts import TBK_DIR, LAST_OUTPUT

def main(_) -> None:
    os.mkdir(TBK_DIR)
    with open(LAST_OUTPUT, 'w') as outfile:
        pass # touch the file

def setup(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    parser = subparsers.add_parser('init')
    parser.set_defaults(func=main)
