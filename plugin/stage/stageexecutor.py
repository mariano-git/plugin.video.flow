from piggy.base.util.logging import Logger
from plugin.stage import Stage
from plugin.stage.executioncontext import ExecutionContext


class StageExecutor:
    __logger__ = Logger.getLogger(f'{__name__}.{__qualname__}')

    def __init__(self):
        self.root = None
        self.context = ExecutionContext()
        self.current = None

    def configure(self, stage: Stage):
        self.root = stage
        return self

    def contextParam(self, name: str, value: object):
        self.context.param(name, value)
        return self

    def execute(self):
        while not self.context.isOver():
            if not self.current:
                self.current = self.root
            current = self.current
            current.execute(self.context)
            if not self.context.isOver():
                self.current = current.next()
