"""Salaries are stored as whole minor units (cents, paise) and shown as decimals."""

from decimal import Decimal

# ponytail: every supported currency has two decimal places. Add a per-currency
# exponent before adding one that does not (JPY, KWD).
MINOR_UNITS = 100


def to_minor(amount: Decimal) -> int:
    return int(amount * MINOR_UNITS)


def to_major(minor: int | float) -> Decimal:
    return Decimal(round(minor)) / MINOR_UNITS
