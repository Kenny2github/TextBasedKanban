from __future__ import annotations
from argparse import _SubParsersAction, ArgumentParser
import os
from ..logic.consts import TBK_DIR

def main(_) -> None:
    os.mkdir(TBK_DIR)

def setup(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    parser = subparsers.add_parser('init')
    parser.set_defaults(func=main)
