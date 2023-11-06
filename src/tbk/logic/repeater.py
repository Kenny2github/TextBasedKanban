from abc import ABC, abstractmethod
from calendar import monthrange
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
import re
from typing import TypeVar
from typing_extensions import override

__all__ = [
    'Repeater',
    'Daily',
    'Weekly',
    'Monthly',
    'Yearly',
    'parse_repeater',
]

DT = TypeVar('DT', bound=datetime | date)

class Repeater(ABC):
    @abstractmethod
    def repeat(self, dt: DT) -> DT:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

@dataclass
class Daily(Repeater):
    step: int = 1

    @override
    def repeat(self, dt: DT) -> DT:
        return dt + timedelta(days=self.step)

    @override
    def __str__(self) -> str:
        if self.step == 1:
            return 'daily'
        return f'every {self.step} days'

@dataclass
class Weekly(Repeater):
    # starts with Monday
    # all False = whatever day is one week from this day
    days_of_week: tuple[bool, bool, bool, bool, bool, bool, bool] \
        = (False, False, False, False, False, False, False)
    step: int = 1

    def __post_init__(self) -> None:
        if any(self.days_of_week) and self.step > 1:
            raise ValueError('Cannot combine multi-week step '
                             'and specific days of week')

    @override
    def repeat(self, dt: DT) -> DT:
        if not any(self.days_of_week):
            return dt + timedelta(days=7 * self.step)
        dt += timedelta(days=1)
        while not self.days_of_week[dt.weekday()]:
            dt += timedelta(days=1)
        return dt

    @override
    def __str__(self) -> str:
        if not any(self.days_of_week):
            if self.step == 1:
                return 'weekly'
            return f'every {self.step} weeks'
        return 'every ' + ', '.join(
            day for i, day in enumerate('Mon Tue Wed Thu Fri Sat Sun'.split())
            if self.days_of_week[i]
        )

@dataclass
class Monthly(Repeater):
    # all days of month to repeat on
    # empty = whatever day is one month from this day (if legal)
    days_of_month: list[int] = field(default_factory=list)
    step: int = 1

    def __post_init__(self) -> None:
        self._check_days(self.days_of_month)
        if self.days_of_month and self.step > 1:
            raise ValueError('Cannot combine multi-month step '
                             'and specific days of month')
        for day in self.days_of_month:
            if day not in range(-28, 29):
                raise ValueError(f'Invalid day of month: {day}')

    @staticmethod
    def _check_days(days: list[int]) -> None:
        if 0 in days:
            raise ValueError('No month has day 0; use -1'
                             'for the last day of the month.')
        for problem in (29, 30, 31, -29, -30, -31):
            if problem in days:
                possibilities = (
                    (-1, -2, -3)[:32 - problem]
                    if problem > 0 else (1, 2, 3)[:32 + problem]
                )
                raise ValueError(
                    f'Not all months have day {problem}; did you mean to use '
                    f'"every {possibilities} of the month"?')

    @override
    def repeat(self, dt: DT) -> DT:
        if not self.days_of_month:
            self._check_days([dt.day])
            month = dt.month + self.step
            year = dt.year
            while month > 12:
                month -= 12
                year += 1
            return dt.replace(year=year, month=month)
        days: list[int] = []
        while dt.day not in days:
            _, last_monthday = monthrange(dt.year, dt.month)
            # convert negative days to days from end of month
            days = [day if day > 0 else last_monthday + day + 1
                    for day in self.days_of_month]
            dt += timedelta(days=1)
        return dt

    @override
    def __str__(self) -> str:
        if not self.days_of_month:
            if self.step == 1:
                return 'monthly'
            return f'every {self.step} months'
        days = ', '.join(map(str, self.days_of_month))
        return f'every {days} of the month'

@dataclass
class Yearly(Repeater):
    step: int = 1

    @override
    def repeat(self, dt: DT) -> DT:
        return dt.replace(year=dt.year + self.step)

    @override
    def __str__(self) -> str:
        if self.step == 1:
            return 'yearly'
        return f'every {self.step} years'

def parse_repeater(s: str) -> Repeater:
    s = s.casefold()
    if 'year' in s:
        if m := re.search(r'\d+', s):
            # assume "every X years"
            return Yearly(int(m.group(0)))
        # assume "every year" or "yearly"
        return Yearly()
    if 'month' in s:
        numbers = list(map(int, re.findall(r'[+-]?\d+', s)))
        if not numbers:
            # assume "every month" or "monthly"
            return Monthly()
        if len(numbers) > 1:
            # assume list of days of month
            return Monthly(numbers)
        if 'of' in s:
            # assume "every X of month" instead of "every X months"
            return Monthly(numbers)
        return Monthly(step=numbers[0])
    if any(word in s for word in
           'mon tue wed thu fri sat sun week'.split()):
        if m := re.search(r'\d+', s):
            # assume "every X weeks"
            return Weekly(step=int(m.group(0)))
        weekdays = (
            'mon' in s, 'tue' in s, 'wed' in s,
            'thu' in s, 'fri' in s, 'sat' in s, 'sun' in s
        )
        return Weekly(weekdays)
    if 'day' in s or 'daily' in s:
        if m := re.search(r'\d+', s):
            # assume "every X days"
            return Daily(int(m.group(0)))
        # assume "every day" or "daily"
        return Daily()
    raise ValueError(f'Could not parse {s!r} as repeat string')
