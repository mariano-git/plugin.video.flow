from piggy.base.util.logging import Logger
from plugin.stage import Stage
from plugin.stage.stageexecutor import StageExecutor


class ServiceExecutor(StageExecutor):
    __logger__ = Logger.getLogger(f'{__name__}.{__qualname__}')

    def __init__(self):
        super().__init__()
        self.monitor = None
        self.over = False
        self.root = None
        self.current = None

    def observes(self, monitor) -> 'ServiceExecutor':
        self.monitor = monitor
        return self

    def configure(self, stage: Stage) -> 'ServiceExecutor':
        self.root = stage
        return self

    def _proceed(self):
        if self.context.isOver():
            self.over = True
            return
        if not self.current:
            self.current = self.root
        current = self.current
        current.execute(self.context)

        self.current = current.next()

    def execute(self):
        self.__logger__.debug('start')

        while not self.monitor.abortRequested() and not self.over:
            self.__logger__.debug('running will waitForAbort for: %s seconds',self.context.throttle)
            if not self.monitor.waitForAbort(self.context.throttle):
                self.__logger__.debug('running - monitor: %s, context: %s, eval: %s', self.monitor.abortRequested(),
                                      self.over, self.monitor.abortRequested() or not self.over)
                self._proceed()
            else:
                self.__logger__.debug('Kodi Abort requested - Exiting...')

        self.__logger__.debug('Exiting main loop...')
