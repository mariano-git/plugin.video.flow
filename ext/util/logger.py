import traceback

import xbmc
import sys

NAME = "plugin.video.flow"
VERSION = 1


class Logger:
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

    def debug(s):
        xbmc.log("[%s v%s] %s" % (NAME, VERSION, s), level=xbmc.LOGDEBUG)

    def log(s):
        xbmc.log("[%s v%s] %s" % (NAME, VERSION, s), level=xbmc.LOGINFO)

    def log_error(message=None):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if message:
            exc_value = message
        xbmc.log("[%s v%s] ERROR: %s (%d) - %s" % (
            NAME, VERSION, exc_traceback.tb_frame.f_code.co_name, exc_traceback.tb_lineno, exc_value),
                 level=xbmc.LOGERROR)

        traceback.print_exc()
