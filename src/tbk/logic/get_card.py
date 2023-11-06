import os
from pathlib import Path
import pickle
from typing import Union
import yaml

from .consts import LAST_STATUS, ROOT_CARD, TBK_DIR
from .card import Card

__all__ = [
    'get_card',
]

def get_card(num_or_title: Union[int, str]) -> Card:
    if isinstance(num_or_title, int):
        if num_or_title <= 0:
            raise ValueError('cannot have negative card numbers')
        with open(LAST_STATUS, 'rb') as f:
            last_status: list[Card] = pickle.load(f)
        return last_status[num_or_title - 1]
    if not num_or_title.endswith('.yaml'):
        num_or_title += '.yaml'
    title = Path(num_or_title)
    try:
        os.stat(title)
    except FileNotFoundError:
        pass # handled later
    else:
        with open(title) as f:
            data = yaml.load(f, yaml.Loader)
        return Card.from_yaml(title.as_posix().removesuffix('.yaml'), data)
    candidates: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(Path('.')):
        dirpath = Path(dirpath)
        if dirpath.name == TBK_DIR.name:
            continue # nothing to see here
        try:
            dirnames.remove(TBK_DIR.name)
        except ValueError:
            pass # already not there

        for card_name in filenames:
            if not card_name.endswith('.yaml'):
                continue
            if card_name == title.name:
                candidates.append(dirpath / card_name)
        for card_name in dirnames:
            if card_name == title.name.removesuffix('.yaml'):
                candidates.append(dirpath / card_name / ROOT_CARD)
    if len(candidates) > 1:
        raise TypeError(
            f'Multiple candidates for {title.name!r}. Did you mean one of these?\n'
            + '\n'.join(path.as_posix() for path in candidates)
        )
    if not candidates:
        raise FileNotFoundError(f'Could not find {title.name!r}')
    with open(candidates[0]) as f:
        data = yaml.load(f, yaml.Loader)
    card = Card.from_yaml(candidates[0].as_posix().removesuffix('.yaml'), data)
    return card
