from threading import Lock


def isBlank(string):
    if string is not None and len(string.strip()) > 0:
        return False
    return True


class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances = {}

    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        # Now, imagine that the program has just been launched. Since there's no
        # Singleton instance yet, multiple threads can simultaneously pass the
        # previous conditional and reach this point almost at the same time. The
        # first of them will acquire lock and will proceed further, while the
        # rest will wait here.
        with cls._lock:
            # The first thread to acquire the lock, reaches this conditional,
            # goes inside and creates the Singleton instance. Once it leaves the
            # lock block, a thread that might have been waiting for the lock
            # release may then enter this section. But since the Singleton field
            # is already initialized, the thread won't create a new object.
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance

        return cls._instances[cls]


class ModelHelper(object):
    def __init__(self, **model):
        object.__setattr__(self, '_ModelHelper__dict', model)

        # Dictionary-like access / updates

    def __getitem__(self, name):
        value = self.__dict[name] if name in self.__dict else None
        if isinstance(value, dict):  # recursively view sub-dicts as objects

            value = ModelHelper(**value)
        return value

    def __setitem__(self, name, value):
        self.__dict[name] = value

    def __delitem__(self, name):
        del self.__dict[name]

        # Object-like access / updates

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self.__dict)

    def __str__(self):
        return str(self.__dict)

    def to_dict(self):
        return self.__dict


# Python datetime sucks
import datetime as Calendar
from datetime import time as Time, timezone as TimeZone, date as Date, datetime as DateTime, timedelta as TimeDelta


class TimeUtils:
    def __init(self, relative: int = None):
        self.relative: relative

    def getTZ(self, hoursDelta: int = 0):
        tzdelta = TimeDelta(hours=hoursDelta)
        # tzname = DateTime.now(TimeZone(tzdelta).astimezone()
        return TimeZone(tzdelta, 'UTC')

    def currentMillis(self):
        current = int(DateTime.now().timestamp() * 1000)
        return current

    def formatMills(self, millis: int, dateformat: str = '%Y%m%d%H%M%S %z', tz=None):
        if tz is None:
            tz = self.getTZ(-3)
        ms = millis / 1000
        ts = DateTime.fromtimestamp(ms, tz).strftime(dateformat)
        return ts

    def toMillis(self, strDateTime: str, format='%Y-%m-%d %H:%M:%S.%f'):
        dt = DateTime.strptime(strDateTime, format)
        millis = dt.timestamp() * 1000
        return int(millis)

    def delta(self, millisMin: int, millisMax: int):
        min: int = DateTime.fromtimestamp(millisMin / 1000)
        max: int = DateTime.fromtimestamp(millisMax / 1000)
        delta = max - min
        return delta.total_seconds() / 3600

    def yesterday(self, string=False, frmt='%Y-%m-%d'):
        yesterday = DateTime.now() - TimeDelta(1)
        if string:
            return yesterday.strftime(frmt)
        return yesterday

    def today(self, string=False, frmt='%Y-%m-%d'):
        today = DateTime.now()
        if string:
            return today.strftime(frmt)
        return today

    def tomorrow(self, string=False, frmt='%Y-%m-%d'):
        yesterday = DateTime.now() + TimeDelta(1)
        if string:
            return yesterday.strftime(frmt)
        return yesterday
