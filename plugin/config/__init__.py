from typing import Dict, Type, TypeVar, cast, Optional, Final, Tuple

from piggy.base.util import Objects
from piggy.base.util.concurrent.timeunit import TimeUnit
from piggy.base.util.date import Date
from piggy.base.util.logging import Logger
from plugin import ADDON
from plugin.util.time import Time

T = TypeVar('T')


class Settings:
    __lg__ = Logger.getLogger(f'{__name__}.{__qualname__}')
    __INSTANCES__: Dict[Type, object] = {}

    def __init__(self):
        self.prefix = self.__PREFIX__

    @staticmethod
    def of(cls: Type[T]) -> T:
        instance = Settings.__INSTANCES__.get(cls)
        if instance is None:
            instance = cls()
            Settings.__INSTANCES__[cls] = instance
        return cast(T, instance)

    def get(self, key):
        name = key[0]
        cls = key[1]
        keyVal = f'{self.prefix}.{name}'
        setting = ADDON.getSetting(keyVal)

        # Kodi returns an "empty" string when value doesn't exists
        if Objects.isEmpty(setting):
            return None
        if name == 'last' or name == 'duration':
            return int(setting)
        if cls == str:
            return setting
        elif cls == bool:
            value = ADDON.getSettingBool(keyVal)
        elif cls == float:
            return float(setting)
        elif cls == int:
            return int(setting)
        # Give up and return what we get in first place
        return setting

    def set(self, key, value):
        name = key[0]
        cls = key[1]
        keyVal = f'{self.prefix}.{name}'

        # Just save value as it is...
        # typed methods doesn't work very well.
        if value is None:
            ADDON.setSetting(keyVal, value)
            return
        if name.startswith('last') or name == 'duration':
            ADDON.setSettingString(keyVal, str(value))
            return

        if cls == int:
            try:
                # Knowing python doesn't have different ints Kodi complains if the number is a long
                # Won't be so hard to save it as long just in case or test the case...
                ADDON.setSettingInt(keyVal, value)
            except OverflowError as o:
                ADDON.setSettingString(keyVal, value)
        elif cls == float:
            ADDON.setSettingNumber(keyVal, value)
        elif cls == bool:
            ADDON.setSettingBool(keyVal, value)
        else:
            ADDON.setSettingString(keyVal, str(value))


class Expirable(Settings):

    def __init__(self):
        super().__init__()

    def getThresholdValue(self) -> int:
        return self.get(self.REFRESH_INTERVAL)

    def getThresholdAsMillis(self) -> int:
        timeUnit = self.REFRESH_INTERVAL[2]
        return timeUnit.toMillis(self.getThresholdValue())

    def getLast(self) -> int:
        return self.get(self.LAST)

    def setLast(self, value: Optional[int] = None):
        return self.set(self.LAST, Date().getTime() if value is None else value)

    def setDuration(self, value: int):
        return self.set(self.DURATION, value)

    def getDuration(self) -> int:
        return self.get(self.DURATION, int)

    def isEnabled(self, key):
        self.get(key)

    def isCurrent(self):
        # TODO implement duration evaluation too
        since = self.getLast()
        if Objects.isEmpty(since):
            return False
        now = Date()
        expire = Date(since + self.getThresholdAsMillis())
        valid = expire.after(now)
        return valid

    def revoke(self, scope=None):
        if scope is None:
            scope = self.REVOKE_ALL
        for r in scope:
            self.set(r, None)


class Access(Settings):
    __PREFIX__ = 'access'
    USERNAME = ('user.name', str)
    PASSWORD = ('user.password', str)

    TV_RATING = ('profile.tvrating', int)
    EXTERNAL_ID = ('profile.external.id', str)

    CAS_ID = ('device.cas.id', str)
    VUID = ('device.vuid', str)
    DEVICE_ID = ('device.id', str)

    REVOKE_ALL: Final[Tuple] = (USERNAME, PASSWORD, CAS_ID, VUID, DEVICE_ID, EXTERNAL_ID, TV_RATING)
    REVOKE_IDS: Final[Tuple] = (CAS_ID, VUID, DEVICE_ID, EXTERNAL_ID, TV_RATING)


class ApiData(Settings):
    __PREFIX__ = 'api.data'
    VERSION = ('version', str)  # api.data.version, str
    TYPE = ('type', str)  # api.data.type, str
    PLAYER = ('player', str)  # api.data.player, str
    NETWORK = ('network', str)  # api.data.network, str
    DEVICE_TYPE = ('device.type', str)  # api.data.device.type, str
    DEVICE_MODEL = ('device.model', str)  # api.data.device.model, str
    DEVICE_NAME = ('device.name', str)  # api.data.device.name, str
    PLATFORM = ('device.platform', str)  # api.data.device.platform, str
    COMPANY = ('company', str)  # api.data.company, str
    REQUEST_ID_PREFIX = ('request.id.prefix', str)


class ApiServers(Settings):
    __PREFIX__ = 'api.servers'
    MAIN = ('main', str)
    IMAGES = ('images', str)
    APP = ('app', str)
    RADIO_APP = ('radio.app', str)
    RADIO_SRC = ('radio.src', str)
    RADIO_IMG = ('radio.img', str)


class Epg(Settings):
    __PREFIX__ = 'epg.pvr'
    PATH = ('path', str)
    XML_EPG_FILE = ('xml.file', str)
    M3U_EPG_FILE = ('m3u.file', str)


class Channels(Expirable):
    __PREFIX__ = 'epg.channels'
    LAST = ('last', int)
    REFRESH_INTERVAL = ('refresh.interval', int, TimeUnit.DAYS)
    SHOW_PROGRESS = ('show.progress', bool)
    GROUP_NAME = ('channels.group.name', str)


class Programs(Expirable):
    __PREFIX__ = 'epg.programs'
    REFRESH_INTERVAL = ('refresh.interval', int, TimeUnit.HOURS)
    LAST = ('last', int)
    LAST_RUN = ('last.run', int)
    LAST_RUN_INTERVAL = ('last.run.interval', int, TimeUnit.HOURS)

    SHOW_PROGRESS = ('show.progress', bool)

    NORMAL_CHANNELS_PER_QUERY = ('normal.channels.per.query', int)
    NORMAL_PROGRAMS_PER_QUERY = ('normal.programs.per.query', int)
    NORMAL_QUERIES_PER_RUN = ('normal.queries.per.run', int)
    NORMAL_WAIT_PER_RUN = ('normal.wait.per.run', int)
    NORMAL_TOTAL_HOURS = ('normal.total.hours', int)

    '''
    EMERGENCY_ENABLED = ('emergency.programs.emergency.enabled', bool)
    EMERGENCY_SHOW_PROGRESS = ('emergency.show.progress', bool)
    EMERGENCY_CHANNELS_PER_QUERY = ('emergency.channels.per.query', int)
    EMERGENCY_PROGRAMS_PER_QUERY = ('emergency.programs.per.query', int)
    EMERGENCY_QUERY_PER_RUN = ('emergency.queries.per.run', int)
    EMERGENCY_WAIT_PER_RUN = ('emergency.wait.per.run', int)
    EMERGENCY_TOTAL_HOURS = ('emergency.total.hours', int)
    '''

    def updateLastRun(self, value: Optional[int] = None):
        return self.set(self.LAST_RUN, Date().getTime() if value is None else value)

    def isRunAllowed(self):
        timeUnit = self.LAST_RUN_INTERVAL[2]
        interval = self.get(self.LAST_RUN_INTERVAL)
        lastRun = self.get(self.LAST_RUN)
        if lastRun > 0:
            lastDate = Date(self.getLast())
            lastRunDate = Date(lastRun)
            if lastDate.after(lastRunDate):
                # Correct condition
                # deltaLastRun must be large enough to fit refresh interval. Minimum 6 otherwise set to 6
                deltaLastRun = Time.ofDate(lastDate).delta(Time.ofDate(lastRunDate), TimeUnit.HOURS)
                if deltaLastRun < 6:
                    self.__lg__.warning(
                        'Delta between last EPG refresh run (%s) and the start of the furthermost TV program'
                        'is very small. I\'ll to correct it...', deltaLastRun
                    )
                    # Do we have correct settings to update EPG programs? If deltaLastRun is small might be because
                    # EPG retrieval period is very small.
                    epgTotalHours = self.get(self.NORMAL_TOTAL_HOURS)
                    refreshInterval = self.get(self.REFRESH_INTERVAL)
                    if epgTotalHours < 24:
                        self.set(self.NORMAL_TOTAL_HOURS, 48)
                    if refreshInterval < 6:
                        self.set(self.REFRESH_INTERVAL, 6)

            return Date().after(Time.ofDate(lastRunDate).add(interval, timeUnit).toDate())
        return True

    def isTVScheduleCurrent(self):
        # Programs last is the startTime of the further most future program
        # So, The schedule isCurrent when that date is still in the future from now + update threshold
        startTimeInFuture = Date(self.getLast())
        realFuture = Date(Date().getTime() + self.getThresholdAsMillis())
        current = startTimeInFuture.after(realFuture)

        return current


class JWT(Expirable):
    __PREFIX__ = 'access.jwt'
    VALUE = ('value', str)
    LAST = ('last', int)
    DURATION = ('duration', int)
    REFRESH_INTERVAL = ('refresh.interval', int, TimeUnit.HOURS)
    REVOKE_ALL: Final[Tuple] = (VALUE, LAST, DURATION)


class PRM(Expirable):
    __PREFIX__ = 'access.prm'
    VALUE = ('value', str)
    LAST = ('last', int)
    DURATION = ('duration', int)
    REFRESH_INTERVAL = ('refresh.interval', int, TimeUnit.HOURS)
    REVOKE_ALL: Final[Tuple] = (VALUE, LAST, DURATION)
