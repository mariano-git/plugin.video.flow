from typing import Type

from piggy.base.util.logging import Logger
from piggy.restful.internal.mappropertiesdelegate import MapPropertiesDelegate
from plugin.stage import StageContext, Tracking, T


class ExecutionContext(StageContext, MapPropertiesDelegate):
    __logger__ = Logger.getLogger(f'{__name__}.{__qualname__}')

    def __init__(self):
        super().__init__()
        self.over = False
        self.error = None
        self.throttle = 1
        self.tracking = Tracking()
        self.diverge = None
        self.params = dict()
        self.components = dict()

    def getLogger(self, name):
        return self.__logger__.getChild(name.__class__.__name__)

    def getComponent(self, cls: Type[T]) -> T:
        component = self.components.get(cls)
        if component is None:
            component = cls()
            self.components[cls] = component
        return component

    def abort(self, reason: str):
        self.__logger__.info('Abort request. Reason: %s', reason)
        self.over = True

    def wait(self, seconds: float):
        self.throttle = seconds

    def isOver(self):
        return self.over

    def setError(self, b):
        self.error = b

    def getError(self):
        return self.error

    def getTracking(self) -> Tracking:
        return self.tracking

    def disjoint(self, item):
        self.diverge = item

    def getDisjoint(self):
        diverge = self.diverge
        self.diverge = None
        return diverge

    def param(self, name: str, value: object):
        self.params[name] = value

    def getParam(self, name: str) -> object:
        return self.params.get(name)

    def consumeParam(self, name: str) -> object:
        value = self.params.get(name)
        if value:
            del self.params[name]
        return value
