#!/usr/bin/env python
"""
Date utilities for working with day numbers and months.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : dateutils
# @created     : Saturday Aug 09, 2025 13:41:02 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
from datetime import datetime

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def is_leap_year(year: int) -> bool:
    """Check if a year is a leap year."""
    if year % 4 != 0:
        return False
    elif year % 100 != 0:
        return True
    else:
        return year % 400 == 0

def get_month_and_day(year: int, day_num: int) -> tuple[str, int]:
    """Get month name and day of month from day of year."""
    date = datetime(year, 1, 1) + timedelta(days=day_num - 1)
    return MONTHS[date.month - 1], date.day

def validate_day_range(year: int, start_day: int, end_day: int) -> None:
    """Validate the day range is within bounds for the year."""
    max_days = 366 if is_leap_year(year) else 365
    if start_day < 1 or end_day > max_days:
        raise ValueError(f"Day range must be between 1 and {max_days}")
    if start_day > end_day:
        raise ValueError("Start day must be less than or equal to end day")
