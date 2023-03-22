import datetime


def to_minute(t):
    return ((t.hour * 60 + t.minute) * 60 + t.second) // 60


def add_time(t1, t2):
    minute = to_minute(t1) + to_minute(t2)
    return datetime.time(minute // 60, minute % 60)
