from __future__ import annotations
from argparse import _SubParsersAction, ArgumentParser
import os
from pathlib import Path
from pprint import pprint
import yaml

from ..logic.card import Card
from ..logic.consts import ROOT_CARD, TBK_DIR

def main(_) -> None:
    for dirpath, dirnames, filenames in os.walk(Path('.')):
        dirpath = Path(dirpath)
        if dirpath.name == TBK_DIR.name:
            continue # don't walk our guts
        try:
            dirnames.remove(TBK_DIR.name)
        except ValueError:
            pass # not there in the first place
        for card_name in filenames:
            if not card_name.endswith('.yaml'):
                continue
            card_name = dirpath / card_name
            print(card_name.parent if card_name.name == ROOT_CARD
                  else str(card_name).removesuffix('.yaml'))
            with open(card_name) as f:
                data = yaml.load(f, yaml.Loader)
            card = Card.from_yaml(data)
            pprint(card)

def setup(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    parser = subparsers.add_parser('status')
    parser.set_defaults(func=main)
