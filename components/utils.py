from datetime import datetime, time
from components.constants import *


def to_minute(t):
    return ((t.hour * 60 + t.minute) * 60 + t.second) // 60


def add_time(t1, t2):
    minute = to_minute(t1) + to_minute(t2)
    return time(minute // 60, minute % 60)


def str_to_datetime(instr):
    return datetime.strptime(instr, DATETIME_FORMAT)


def str_to_time(instr):
        dt = datetime.strptime(instr, TIME_FORMAT)
        return time(dt.hour, dt.minute, dt.second)
