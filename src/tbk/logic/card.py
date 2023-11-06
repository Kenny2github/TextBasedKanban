from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
import re
from typing import Self

from .repeater import Repeater, parse_repeater

__all__ = [
    'Status',
    'Card',
]

class Status(Enum):
    # normalized to have no spaces
    BACKLOG = 'backlog'
    TO_DO = 'todo'
    AWAITING_MEETING = 'awaitingmeeting'
    IN_PROGRESS = 'inprogress'
    BLOCKED = 'blocked'

    @property
    def pretty(self) -> str:
        return self.name.replace('_', ' ').title()

    def __lt__(self, other: Self) -> bool:
        if self == other:
            return False
        for value in type(self):
            if value == self:
                return True
            if value == other:
                return False
        return NotImplemented

@dataclass(kw_only=True)
class Card:
    title: str
    status: Status = Status.BACKLOG
    due: datetime | date | None = None
    repeat: Repeater | None = None
    estimate: int | None = None
    reminder: list[datetime] = field(default_factory=list)
    start: datetime | date | None = None

    def __lt__(self, other: Self) -> bool:
        if self.due is not None:
            if other.due is not None:
                return self.due < other.due
            return True # with due date < without due date
        if other.due is not None:
            return False # guaranteed self.due is None
        # both None, check reminder
        if self.reminder:
            if other.reminder:
                return min(self.reminder) < min(other.reminder)
            return True # with reminder < without reminder
        if other.reminder:
            return False # guaranteed not self.reminder
        # both empty, check start
        if self.start is not None:
            if other.start is not None:
                return self.start < other.start
            return True # with start date < without start date
        if other.start is not None:
            return False # guaranteed self.start is None
        # both empty, check status
        if self.status != other.status:
            return self.status < other.status
        # same status, check estimate
        return (self.estimate or 0) < (other.estimate or 0)

    @classmethod
    def from_yaml(cls: type[Self], title: str, d: dict) -> Self:
        d = d.copy()
        kwargs = {}
        if 'status' in d:
            kwargs['status'] = Status(re.sub(r'\s*', '', d.pop('status').casefold()))
        if 'due' in d:
            kwargs['due'] = d.pop('due')
        if 'repeat' in d:
            kwargs['repeat'] = parse_repeater(d.pop('repeat'))
        if 'estimate' in d:
            kwargs['estimate'] = d.pop('estimate')
        if 'reminder' in d:
            kwargs['reminder'] = d.pop('reminder')
            if not isinstance(kwargs, list):
                kwargs['reminder'] = [kwargs['reminder']]
        if 'start' in d:
            kwargs['start'] = d.pop('start')
        if d:
            raise ValueError(f'Unexpected extra data: {d}')
        return cls(title=title, **kwargs)

    def to_yaml(self) -> dict:
        d = {}
        # insertion order is serialization order
        d['status'] = self.status.pretty
        if self.due is not None:
            d['due'] = self.due
        if self.repeat is not None:
            d['repeat'] = str(self.repeat)
        if self.estimate is not None:
            d['estimate'] = self.estimate
        if len(self.reminder) > 1:
            d['reminder'] = self.reminder
        elif self.reminder:
            d['reminder'] = self.reminder[0]
        if self.start is not None:
            d['start'] = self.start
        return d

    def do_repeat(self) -> None:
        if self.repeat is None:
            return
        if self.due is not None:
            due_date = self.due.date() if isinstance(self.due, datetime) else self.due
            reminders = [reminder.date() for reminder in self.reminder]
            start = self.start.date() if isinstance(self.start, datetime) else self.start

            reminder_deltas = [due_date - reminder for reminder in reminders]
            start_delta = (due_date - start) if start is not None else None

            while self.due <= date.today():
                self.due = self.repeat.repeat(self.due)
            self.reminder = [datetime.combine(self.due - delta, reminder.time())
                             for delta, reminder in zip(reminder_deltas, self.reminder)]
            if start_delta is not None:
                if isinstance(self.start, datetime):
                    self.start = datetime.combine(
                        self.due - start_delta, self.start.time())
                elif isinstance(self.due, datetime):
                    self.start = self.due.date() - start_delta
                else:
                    self.start = self.due - start_delta
            return
        if self.start is not None:
            start = self.start.date() if isinstance(self.start, datetime) else self.start

            deltas = [start - reminder.date() for reminder in self.reminder]
            while self.start <= date.today():
                self.start = self.repeat.repeat(self.start)
            self.reminder = [datetime.combine(self.start - delta, reminder.time())
                             for delta, reminder in zip(deltas, self.reminder)]
            return
        # only reminder might not be empty
        while any(r <= date.today() for r in self.reminder):
            self.reminder = list(map(self.repeat.repeat, self.reminder))
