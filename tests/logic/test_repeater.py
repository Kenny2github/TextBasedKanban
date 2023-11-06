from datetime import date, datetime
import pytest

from tbk.logic.repeater import *

def test_daily() -> None:
    repeater = Daily()
    assert repeater.repeat(date(2023, 11, 6)) == date(2023, 11, 7)

    repeater = Daily(2)
    assert repeater.repeat(date(2023, 11, 6)) == date(2023, 11, 8)

    assert repeater.repeat(date(2023, 11, 30)) == date(2023, 12, 2)

def test_weekly() -> None:
    repeater = Weekly()
    assert repeater.repeat(date(2023, 11, 6)) == date(2023, 11, 13)

    repeater = Weekly(step=2)
    assert repeater.repeat(date(2023, 11, 6)) == date(2023, 11, 20)

    #                  Mon    Tue    Wed   Thu    Fri    Sat    Sun
    repeater = Weekly((False, False, True, False, False, False, True))
    assert repeater.repeat(date(2023, 11, 5)) == date(2023, 11, 8)
    assert repeater.repeat(date(2023, 11, 6)) == date(2023, 11, 8)
    assert repeater.repeat(date(2023, 11, 8)) == date(2023, 11, 12)

    with pytest.raises(ValueError):
        repeater = Weekly(repeater.days_of_week, 2)

def test_monthly() -> None:
    repeater = Monthly()
    assert repeater.repeat(date(2023, 11, 6)) == date(2023, 12, 6)

    repeater = Monthly(step=2)
    assert repeater.repeat(date(2023, 11, 6)) == date(2024, 1, 6)

    repeater = Monthly([1, 15, -1]) # first, 15th, and last
    assert repeater.repeat(date(2023, 11, 6)) == date(2023, 11, 15)
    assert repeater.repeat(date(2023, 11, 15)) == date(2023, 11, 30)
    assert repeater.repeat(date(2023, 12, 15)) == date(2023, 12, 31)

    with pytest.raises(ValueError):
        repeater = Monthly([0])
    with pytest.raises(ValueError):
        repeater = Monthly([31])
    with pytest.raises(ValueError):
        repeater = Monthly([-31])
    with pytest.raises(ValueError):
        repeater = Monthly([32])

def test_yearly() -> None:
    repeater = Yearly()
    assert repeater.repeat(date(2023, 11, 6)) == date(2024, 11, 6)

    repeater = Yearly(2)
    assert repeater.repeat(date(2023, 11, 6)) == date(2025, 11, 6)

def test_datetime() -> None:
    repeater = Daily()
    assert repeater.repeat(datetime(2023, 11, 6)) == datetime(2023, 11, 7)
    repeater = Weekly()
    assert repeater.repeat(datetime(2023, 11, 6)) == datetime(2023, 11, 13)
    repeater = Monthly()
    assert repeater.repeat(datetime(2023, 11, 6)) == datetime(2023, 12, 6)
    repeater = Yearly()
    assert repeater.repeat(datetime(2023, 11, 6)) == datetime(2024, 11, 6)

@pytest.mark.parametrize(
    ('input', 'output'),
    (
        ('year', 'yearly'),
        ('2 years', 'every 2 years'),
        ('month', 'monthly'),
        ('2 month', 'every 2 months'),
        ('2 of month', 'every 2 of the month'),
        ('week', 'weekly'),
        ('week 2', 'every 2 weeks'),
        ('Sunday Wednesday', 'every Wed, Sun'),
        ('day', 'daily'),
        ('daily', 'daily'),
        ('day 2', 'every 2 days')
    )
)
def test_parse_repeater(input: str, output: str) -> None:
    assert str(parse_repeater(input)) == output
