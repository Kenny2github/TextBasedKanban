from __future__ import annotations
from argparse import _SubParsersAction, ArgumentParser
import os
from pathlib import Path
import yaml

from ..logic.card import Card
from ..logic.consts import ROOT_CARD, TBK_DIR
from ..utils.graphics import str_table

__all__ = [
    'setup',
]

def main(_) -> None:
    cards: list[Card] = []
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
            with open(card_name) as f:
                data = yaml.load(f, yaml.Loader)
            card = Card.from_yaml(str(
                card_name.parent if card_name.name == ROOT_CARD
                else str(card_name).removesuffix('.yaml')
            ), data)
            cards.append(card)
    cards.sort()

    table: list[list[object]] = [['#', 'Status', 'Est', 'Due', 'Name']]
    for i, card in enumerate(cards, start=1):
        status = card.status.pretty
        due = '' if card.due is None else card.due
        table.append([i, status, card.estimate, due, card.title])
    print(str_table(table, [1, 0, 1, -1, -1]))

def setup(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    parser = subparsers.add_parser('status')
    parser.set_defaults(func=main)
