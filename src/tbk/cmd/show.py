from __future__ import annotations
import sys
from argparse import _SubParsersAction, ArgumentParser
import yaml

from ..logic.get_card import get_card

__all__ = [
    'setup',
]

class _ShowArgs:
    card: str

def main(args: _ShowArgs) -> None:
    if args.card.startswith('#'):
        card = int(args.card.removeprefix('#'))
    else:
        card = args.card
    try:
        card = get_card(card)
    except (TypeError, FileNotFoundError) as exc:
        sys.exit('error: ' + str(exc))
    print(card.title)
    yaml.dump(card.to_yaml(), sys.stdout, sort_keys=False)

def setup(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    parser = subparsers.add_parser('show')
    parser.set_defaults(func=main)
    parser.add_argument(
        'card', help='the card to show; #x from last tbk status, or title.')
