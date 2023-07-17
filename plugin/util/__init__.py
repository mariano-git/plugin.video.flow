from typing import Generic, TypeVar, List
from urllib.parse import urlparse, parse_qs

import xbmcvfs
from xbmcgui import DialogProgressBG

from piggy.base.util import Objects
from piggy.base.util.logging import Logger


class File:
    def __init__(self, path: List[str]):
        self.path = path

    @staticmethod
    def of(*args: str):
        path = list()
        for p in args:
            path.extend(p.split('/'))
        return File(path)

    def exists(self):
        return xbmcvfs.exists(self.toString())

    def append(self, path: str):
        newPath = list(self.path)
        newPath.append(path)
        return File(newPath)

    def toString(self):
        return xbmcvfs.makeLegalFilename(xbmcvfs.translatePath('/'.join(self.path)))


# TODO Remove Command and Handler
class Command:
    def __init__(self, args):
        # FIXME Export handle like verb
        # 'plugin://plugin.video.flow/play', '1', '?program=751664758800&type=TV_SCHEDULE', 'resume:false'
        trail = f"?{args[3].replace(':', '=')}" if Objects.isEmpty(
            args[2]) else f"{args[2]}&{args[3].replace(':', '=')}"
        cmdUri = urlparse(f"{args[0]}{trail}")
        self.handle: int = int(args[1])
        self.verb: str = None if Objects.isEmpty(cmdUri.path.lstrip('/')) else cmdUri.path.lstrip('/')
        self.arguments: dict = self.simplify(parse_qs(cmdUri.query))

    def simplify(self, params):
        values = {}
        for key, value in params.items():
            values[key] = value if len(value) > 1 else value[0]
        return values

    def __str__(self):
        return f"Command[handle: {self.handle}, verb: {self.verb}, args: {self.arguments}]"


class Handler:
    def process(self, command: Command):
        pass


T = TypeVar('T')
R = TypeVar('R')


class Converter(Generic[T, R]):
    def convert(self, source: T) -> R:
        pass


class ProgressIndicator(DialogProgressBG):
    __lg__ = Logger.getLogger(f'{__name__}.{__qualname__}')

    def __init__(self, total: int = None, heading=None, message=None):
        super().__init__()
        self.heading = heading
        self.message = message
        self.total = total
        self.count = 0

    def create(self, heading: str, message: str = ""):
        super().create(heading, message)
        self.heading = heading
        self.message = message

    def setTotal(self, total: int):
        self.total = total

    def refresh(self, amount: int):
        self.count += amount
        self.__lg__.debug('total: %s, count: %s', self.total, self.count)
        super().update(int(self.count * 100 / self.total))

    def done(self):
        super().close()

    @classmethod
    def of(cls, total, heading, message):
        return ProgressIndicator(total, heading, message)

    @classmethod
    def ofNull(cls):
        class NullProgressDialog(DialogProgressBG):
            def __init__(self, finish=False):
                self.finish = finish

            def deallocating(self):
                pass

            def create(self, heading: str, message: str = ""):
                self.finish = True

            def update(self, percent: int = 0,
                       heading: str = "",
                       message: str = "") -> None:
                pass

            def close(self) -> None:
                self.finish = True

            def isFinished(self) -> bool:
                return self.finish

            def setTotal(self, total: int):
                pass

            def refresh(self, amount: int):
                pass

            def done(self):
                self.finish = True

        return NullProgressDialog()
