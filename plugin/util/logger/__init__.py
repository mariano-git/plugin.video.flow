import sys
from logging import Handler, getLevelName

import xbmc
from piggy.base.util.logging import Logger


class KodiLoggerHandler(Handler):
    """
     A handler class which writes logging records, appropriately formatted,
     to a stream. Note that this class does not close the stream, as
     sys.stdout or sys.stderr may be used.
     """

    terminator = '\n'

    def __init__(self):
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        Handler.__init__(self)
        self.stream = sys.stderr

    def flush(self):
        """
        Flushes the stream.
        """
        pass

    def getKodiLevel(self, levelno):

        if levelno == Logger.CRITICAL or levelno == Logger.FATAL:
            return xbmc.LOGFATAL
        if levelno == Logger.ERROR:
            return xbmc.LOGERROR
        if levelno == Logger.INFO:
            return xbmc.LOGINFO
        if levelno == Logger.WARN or levelno == Logger.WARNING:
            return xbmc.LOGWARNING
        if levelno == Logger.DEBUG:
            return xbmc.LOGDEBUG
        if levelno == Logger.NOTSET:
            return xbmc.LOGNONE

    def emit(self, record):

        kodiLevel = self.getKodiLevel(record.levelno)

        try:
            msg = self.format(record)
            xbmc.log(f'plugin.video.flow: {msg}', kodiLevel)
        except RecursionError:  # See issue 36272
            raise
        except Exception:
            self.handleError(record)

    def setStream(self, stream):
        """
        Sets the StreamHandler's stream to the specified value,
        if it is different.

        Returns the old stream, if the stream was changed, or None
        if it wasn't.
        """
        if stream is self.stream:
            result = None
        else:
            result = self.stream
            self.acquire()
            try:
                self.flush()
                self.stream = stream
            finally:
                self.release()
        return result

    def __repr__(self):
        level = getLevelName(self.level)
        name = 'KodiLogger'  # getattr(self.stream, 'name', '')
        #  bpo-36015: name can be an int
        name = str(name)
        if name:
            name += ' '
        return '<%s %s(%s)>' % (self.__class__.__name__, name, level)
