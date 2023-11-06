from __future__ import annotations
from argparse import _SubParsersAction, ArgumentParser
import os
from pathlib import Path
import pickle
from typing import Literal, Optional, Self, TypeVar, get_args
import yaml
from rich import print
from rich.table import Table

from ..logic.card import Card
from ..logic.consts import ROOT_CARD, TBK_DIR, LAST_STATUS

__all__ = [
    'setup',
]

_T = TypeVar('_T')
class _EmptyValue:
    def __str__(self) -> str:
        return ''
    def __lt__(self, other: object) -> bool:
        return False
    def __call__(self, value: Optional[_T]) -> _T | Self:
        if value is None:
            return self
        return value
_empty_value = _EmptyValue()

SortKey = Literal[
    'status', '!status',
    'estimate', '!estimate',
    'due', '!due',
]

class _StatusArgs:
    sort: Optional[list[SortKey]]

def get_cards() -> list[Card]:
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
            card = Card.from_yaml(card_name.as_posix().removesuffix('.yaml'), data)
            cards.append(card)
    return cards

def sort_cards(cards: list[Card], sort: list[SortKey]) -> None:
    for key in reversed(sort):
        reverse = key.startswith('!')
        match key:
            case 'status' | '!status':
                cards.sort(key=lambda card: card.status, reverse=reverse)
            case 'estimate' | '!estimate':
                cards.sort(key=lambda card: _empty_value(card.estimate), reverse=reverse)
            case 'due' | '!due':
                cards.sort(key=lambda card: _empty_value(card.due), reverse=reverse)

def print_cards(cards: list[Card]) -> None:
    table = Table(show_header=True)
    table.add_column('#', justify='right')
    table.add_column('Status', justify='center')
    table.add_column('Est', justify='right')
    table.add_column('Due', justify='left')
    table.add_column('Parent(s)', justify='right')
    table.add_column('Title', justify='left')
    for i, card in enumerate(cards, start=1):
        status = card.status.pretty
        due = '' if card.due is None else card.due
        days_left = (card.due - card.due.today()).days # type: ignore
        if card.due is not None and days_left <= 1:
            due = f'[bold red underline]{due}[/]'
        title = Path(card.title)
        if title.name == ROOT_CARD.removesuffix('.yaml'):
            title = title.parent
        table.add_row(
            str(i), status, str(_empty_value(card.estimate)),
            str(due), title.parent.as_posix(), title.name
        )
    print(table)

def main(args: _StatusArgs) -> None:
    cards = get_cards()
    # sort cards
    if args.sort is None:
        cards.sort()
    else:
        sort_cards(cards, args.sort)
    # save this order for other commands to use
    with open(LAST_STATUS, 'wb') as f:
        pickle.dump(cards, f)
    # output pretty table
    print_cards(cards)

def setup(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    parser = subparsers.add_parser('status')
    parser.set_defaults(func=main)
    parser.add_argument(
        '-s', '--sort', nargs='+', choices=get_args(SortKey),
        default=None, help='the key(s) to sort by; ! for reverse order')
