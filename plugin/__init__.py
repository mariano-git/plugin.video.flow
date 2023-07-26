import logging
import uuid
from typing import Final, Tuple

import xbmcaddon

from plugin.util.logger import KodiLoggerHandler

ADDON_ID = 'plugin.video.flow'
ADDON = xbmcaddon.Addon(id=ADDON_ID)
ADDON_VERSION = ADDON.getAddonInfo('version')


class PlugInConstants:
    STREAMING_PROTOCOLS: Final[Tuple[str]] = 'DASH',
    STREAMING_ENCRYPTIONS: Final[Tuple[str]] = 'Widevine',

    VALUE: Final[str] = 'value'

    IPTV_SIMPLE_PLUGIN = 'pvr.iptvsimple'


class PlugInUtils:
    @classmethod
    def refreshEpg(cls):
        addon = xbmcaddon.Addon(PlugInConstants.IPTV_SIMPLE_PLUGIN)
        addon.setSetting('reload', 'reload')

    @staticmethod
    def CASID():
        return str(uuid.uuid4()).replace('-', '')

    @staticmethod
    def initLogger():
        logging.basicConfig(
            format='%(levelname)s: %(name)s: %(message)s',
            level=logging.DEBUG,
            handlers=[KodiLoggerHandler()],
            force=True

        )
        # Logger.getLogger('piggy.base.overload').setLevel(logging.INFO)

        logging.getLogger('piggy.base.notation').setLevel(logging.DEBUG)
        logging.getLogger("urllib").setLevel(logging.DEBUG)
