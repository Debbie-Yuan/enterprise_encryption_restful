import uuid
from datetime import timedelta, datetime


def generate_token(prefix=None):
    return prefix + uuid.uuid4().hex


def generate_timedelta(days=0, seconds=0, minutes=0, hours=0, weeks=0):
    return timedelta(
        days=days,
        seconds=seconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks
    )


def datetime_add(cursor_datetime: datetime, delta: timedelta):
    return cursor_datetime + delta
