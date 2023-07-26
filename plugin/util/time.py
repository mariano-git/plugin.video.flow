from datetime import datetime as DateTime, timedelta as TimeDelta, timezone as TimeZone

from piggy.base.util.concurrent.timeunit import TimeUnit
from piggy.base.util.date import Date


class Time:

    def __init__(self, dt, tz=None):
        self.dt = dt
        self.tz = tz

    @classmethod
    def ofDate(cls, date: Date) -> 'Time':
        return Time(DateTime.fromtimestamp(float(date.getTime() / 1000)))

    @classmethod
    def ofYesterday(cls) -> 'Time':
        return Time(DateTime.now() - TimeDelta(days=1))

    @classmethod
    def ofNow(cls) -> 'Time':
        return Time(DateTime.now())

    @classmethod
    def ofTomorrow(cls) -> 'Time':
        return Time(DateTime.now() + TimeDelta(days=1))

    def atZero(self, unit: TimeUnit = TimeUnit.HOURS) -> 'Time':
        if unit == TimeUnit.NANOSECONDS or unit == TimeUnit.MICROSECONDS or unit == TimeUnit.MILLISECONDS:
            dt = DateTime(self.dt.year, self.dt.month, self.dt.day, self.dt.hour, self.dt.minute, self.dt.second,
                          0, tzinfo=self.tz)
        if unit == TimeUnit.SECONDS:
            dt = DateTime(self.dt.year, self.dt.month, self.dt.day, self.dt.hour, self.dt.minute, 0,
                          0, tzinfo=self.tz)
        if unit == TimeUnit.MINUTES:
            dt = DateTime(self.dt.year, self.dt.month, self.dt.day, self.dt.hour, 0, 0,
                          0, tzinfo=self.tz)
        if unit == TimeUnit.HOURS:
            dt = DateTime(self.dt.year, self.dt.month, self.dt.day, 0, 0, 0,
                          0, tzinfo=self.tz)
        if unit == TimeUnit.DAYS:
            dt = DateTime(self.dt.year, self.dt.month, 1, 0, 0, 0,
                          0, tzinfo=self.tz)
        return Time(dt, self.tz)

    def UTC(self) -> 'Time':
        self.tz = TimeZone.utc
        self.dt = self.dt.replace(tzinfo=self.tz)
        return Time(self.dt, self.tz)

    def add(self, amount: int, unit: TimeUnit) -> 'Time':
        delta = self.toMillis() + unit.toMillis(amount)
        dt = DateTime.fromtimestamp(float(delta / 1000), self.tz)  # .replace(tzinfo=self.tz)
        return Time(dt, self.tz)

    def substract(self, amount, unit: TimeUnit) -> 'Time':
        delta = self.toMillis() - unit.toMillis(amount)
        dt = DateTime.fromtimestamp(float(delta / 1000), self.tz)  # .replace(tzinfo=self.tz)
        return Time(dt, self.tz)

    def delta(self, other: 'Time', unit: TimeUnit) -> float:
        if isinstance(other, Time):
            delta = self.toMillis() - other.toMillis()
            return unit.convert(delta, TimeUnit.MILLISECONDS)
        elif isinstance(other, Date):
            delta = self.toMillis() - other.getTime()
            return unit.convert(delta, TimeUnit.MILLISECONDS)

    def toMillis(self) -> int:
        return int(self.dt.timestamp() * 1000)

    def toDate(self) -> Date:
        return Date(self.toMillis())
