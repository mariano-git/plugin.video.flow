from collections import deque
from typing import Type, TypeVar, Optional

from piggy.base import raisable, Raisable
from piggy.restful.internal.propertiesdelegate import PropertiesDelegate


@raisable
class StageException(Raisable):
    pass


T = TypeVar('T')


class Tracking:
    def __init__(self):
        self.success = deque(set(), 3)
        self.error = deque(set(), 3)

    def addSuccess(self, orchestrator):
        self.success.append(orchestrator)

    def addError(self, orchestrator):
        self.error.append(orchestrator)


class StageContext(PropertiesDelegate):

    def getLogger(self, name):
        pass

    def abort(self, reason: str):
        pass

    def getComponent(self, cls: Type[T]) -> T:
        pass

    def setError(self, b):
        pass

    def getError(self):
        pass

    def wait(self, seconds: float):
        pass

    def getTracking(self) -> Tracking:
        pass

    def disjoint(self, item):
        pass

    def getDisjoint(self):
        pass

    def param(self, name: str, value: object):
        pass

    def getParam(self, name: str) -> object:
        pass

    def consumeParam(self, name: str) -> object:
        pass


class Stage:
    LONG_WAIT = 5
    MEDIUM_WAIT = 2.5
    SMALL_WAIT = .5
    RACE = .1

    def execute(self, context: StageContext) -> Optional[bool]:
        raise NotImplementedError('Needs implementation')
