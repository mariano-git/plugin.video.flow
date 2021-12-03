import uuid

import xbmc
import xbmcaddon
import xbmcvfs

from ext.util import isBlank, TimeUtils
from ext.util.logger import Logger

ADDON_ID = 'plugin.video.flow'
AddOnSettings = xbmcaddon.Addon(id=ADDON_ID)
NAME = AddOnSettings.getAddonInfo('name')
SETTINGS_LOC = AddOnSettings.getAddonInfo('profile')
PATH = AddOnSettings.getAddonInfo('path')
VERSION = AddOnSettings.getAddonInfo('version')
ICON = AddOnSettings.getAddonInfo('icon')
FANART = AddOnSettings.getAddonInfo('fanart')
LANGUAGE = AddOnSettings.getLocalizedString

# Constants

API_VERSION = '3.37.1'
API_TYPE = 'CVA'
API_DEVICE_NAME = 'Linux x86_64'
API_DEVICE_MODEL = 'PC'
API_DEVICE_TYPE = 'WEB'
API_PLAYER_TYPE = "VISUAL_ON"
API_NETWORK_TYPE = "BROADBAND"
API_DEVICE_PLATFORM = 'WINDOWS'  # ?
API_COMPANY = 'flow'
LOGIN_URL = '/auth/v2/provision/login'
CONTENT_SOURCE_URL = 'prm/v1/contentSource'

SETTING_INVALID = 'invalid'
SETTING_USER = 'username'
SETTING_PASSWORD = 'password'
SETTING_BASE_URL = 'baseUrl'
SETTING_CAS_ID = 'clientCasId'
SETTING_JWT = 'jwt'
SETTING_LAST_JWT = 'lastJwt'
SETTING_JWT_THRESHOLD = "jwtThreshold"

SETTING_PRM = 'prm'
SETTING_LAST_PRM = 'lastPrm'
SETTING_PRM_THRESHOLD = "prmThreshold"
DEFAULT_PRM_THRESHOLD = "90"

SETTING_LOGIN_RETRY = 2
SETTING_MULTIRIGHT = 'multiRightVuid'
SETTING_LAST_EPG = 'lastEpg'
SETTING_EPG_THRESHOLD = 'epgThreshold'

DEFAULT_USER = 'DEFAULT_USER'
DEFAULT_PASSWORD = 'DEFAULT_PASSWD'
# DEFAULT_BASE_URL = 'http://localhost:8888'
DEFAULT_BASE_URL = 'https://web.flow.com.ar'
DEFAULT_INT = "0"
DEFAULT_EPG_THRESHOLD = "6"
DEFAULT_JWT_THRESHOLD = "90"  # 1 1/2 Hours But currently I don't know for how long this token can be valid


def getSetting(key: str, default: str = None):
    value = AddOnSettings.getSetting(key)
    if isBlank(value):
        value = default
    return value


def setSetting(key: str, value: str):
    return AddOnSettings.setSetting(id=key, value=value)


def isSettingEnabled(key: str, default: bool):
    value = AddOnSettings.getSettingBool(key)
    if isBlank(value):
        value = default
    return value


def setSettingEnabled(key: str, value: bool):
    return AddOnSettings.setSettingBool(id=key, value=value)


def getUser():
    return getSetting(SETTING_USER, SETTING_INVALID)


def getPassword():
    return getSetting(SETTING_PASSWORD, SETTING_INVALID)


def getBaseUrl():
    return getSetting(SETTING_BASE_URL, DEFAULT_BASE_URL)


def getJwtThreshold():
    return int(getSetting(SETTING_JWT_THRESHOLD, DEFAULT_JWT_THRESHOLD)) * 60000


def getLastJwt():
    return int(getSetting(SETTING_LAST_JWT, DEFAULT_INT))


def setJwt(jwt: str):
    timeUtils: TimeUtils = TimeUtils()
    setSetting(SETTING_JWT, jwt)
    now = timeUtils.currentMillis()
    Logger.debug(f"Saving last jwt timestamp {now}")
    setSetting(SETTING_LAST_JWT, str(now))


def getJwt():
    timeUtils: TimeUtils = TimeUtils()
    lastJwt = getLastJwt()
    lastJwtDelta: int = timeUtils.currentMillis() - lastJwt
    threshold = getJwtThreshold()
    if lastJwtDelta > threshold:
        return None
    return getSetting(SETTING_JWT, SETTING_INVALID)


def getPrmThreshold():
    return int(getSetting(SETTING_PRM_THRESHOLD, DEFAULT_PRM_THRESHOLD)) * 60000


def getLastPrm():
    return int(getSetting(SETTING_LAST_PRM, DEFAULT_INT))


def setPrm(prm: str):
    timeUtils: TimeUtils = TimeUtils()
    setSetting(SETTING_PRM, prm)
    now = timeUtils.currentMillis()
    setSetting(SETTING_LAST_PRM, str(now))


def getPrm():
    timeUtils: TimeUtils = TimeUtils()
    lastPrm = getLastPrm()
    lastPrmDelta: int = timeUtils.currentMillis() - lastPrm
    threshold = getPrmThreshold()
    if lastPrmDelta > threshold:
        return None
    return getSetting(SETTING_PRM, SETTING_INVALID)


def touchJwt():
    timeUtils: TimeUtils = TimeUtils()
    now = timeUtils.currentMillis()
    Logger.debug(f"Saving last jwt timestamp {now}")
    setSetting(SETTING_LAST_JWT, str(now))


def invalidateJwt():
    setSetting(SETTING_JWT, SETTING_INVALID)
    setSetting(SETTING_LAST_JWT, str(DEFAULT_INT))


def setMultiRightVuid(value):
    setSetting(SETTING_MULTIRIGHT, value)


def getMultiRightVuid():
    return getSetting(SETTING_MULTIRIGHT)


def getClientCasId():
    clientCasId = getSetting(SETTING_CAS_ID)
    if isBlank(clientCasId):
        clientCasId = str(uuid.uuid4()).replace('-', '')
        setSetting(SETTING_CAS_ID, clientCasId)

    return clientCasId


def getLastEpg():
    return int(getSetting(SETTING_LAST_EPG, DEFAULT_INT))


def getEpgThreshold():
    return int(getSetting(SETTING_EPG_THRESHOLD, DEFAULT_EPG_THRESHOLD)) * 3600000


def touchEpg():
    timeUtils: TimeUtils = TimeUtils()
    now = timeUtils.currentMillis()
    setSetting(SETTING_LAST_EPG, str(now))


def clearEpg():
    setSetting(SETTING_LAST_EPG, str(0))


def getConfigPath():
    return xbmcvfs.translatePath(SETTINGS_LOC)
