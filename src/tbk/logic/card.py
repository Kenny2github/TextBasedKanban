from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
import re
from typing import Self

from .repeater import Repeater, parse_repeater

class Status(Enum):
    # normalized to have no spaces
    BACKLOG = 'backlog'
    TO_DO = 'todo'
    AWAITING_MEETING = 'awaitingmeeting'
    IN_PROGRESS = 'inprogress'
    BLOCKED = 'blocked'

@dataclass(kw_only=True)
class Card:
    status: Status = Status.BACKLOG
    due: datetime | date | None = None
    repeat: Repeater | None = None
    estimate: int | None = None
    reminder: list[datetime] = field(default_factory=list)
    start: datetime | date | None = None

    @classmethod
    def from_yaml(cls: type[Self], d: dict) -> Self:
        d = d.copy()
        kwargs = {}
        if 'status' in d:
            kwargs['status'] = Status(re.sub(r'\s*', '', d.pop('status')))
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
        return cls(**kwargs)

    def do_repeat(self) -> None:
        if self.repeat is None:
            return
        if self.due is not None:
            due_date = self.due.date() if isinstance(self.due, datetime) else self.due
            reminders = [reminder.date() for reminder in self.reminder]
            start = self.start.date() if isinstance(self.start, datetime) else self.start

            reminder_deltas = [due_date - reminder for reminder in reminders]
            start_delta = (due_date - start) if start is not None else None

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
            self.start = self.repeat.repeat(self.start)
            self.reminder = [datetime.combine(self.start - delta, reminder.time())
                             for delta, reminder in zip(deltas, self.reminder)]
            return
        # only reminder might not be empty
        self.reminder = list(map(self.repeat.repeat, self.reminder))
