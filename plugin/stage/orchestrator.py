from piggy.base import Raisable, IllegalStateException
from piggy.base.util import Objects
from piggy.base.util.logging import Logger
from plugin.stage import Stage, StageContext


class Orchestrator(Stage):
    __logger__ = Logger.getLogger(f'{__name__}.{__qualname__}')

    def __create__(self, element):
        if isinstance(element, type):
            return element()
        return element

    def __init__(self, element):
        self.main = self.__create__(element)
        self.crash = None
        self.success = None
        self.failure = None
        self.other = None
        self.follow = None

    @classmethod
    def getPath(cls, holder, results):
        cls.__logger__.debug('\tLooking next path on: %s, with results: %s', holder, results)
        if results is None:
            cls.__logger__.debug('\tPath is "%s"', holder)
            return holder
        if results:
            cls.__logger__.debug('\tPath is SUCCESS "%s"', holder.success)
            return holder.success
        cls.__logger__.debug('\tPath is OTHER "%s"', holder.other)
        return holder.other

    @classmethod
    def invoke(cls, current, main, crash, context):
        invocation = {'current': current, 'main': main, 'crash': crash, 'value': None}
        cls.__logger__.debug('invoke: %s', invocation)

        if isinstance(main, Orchestrator):
            value = cls.invoke(main, main.main, main.crash, context)
            invocation['value'] = value
            context.getTracking().addSuccess(invocation)
            return value
        try:

            value = cls.getPath(current, main.execute(context))
            cls.__logger__.debug('Executed: %s return: %s', main, value)
            invocation['value'] = value
            context.getTracking().addSuccess(invocation)
            disjoint = context.getDisjoint()
            if disjoint:
                cls.__logger__.debug('--------------- FLOW CHANGE:  -----------------\n'
                                     '                               item: %s\n'
                                     '------------------------------------------------',
                                     disjoint)

                return disjoint

            return value
        except BaseException as exception:
            cls.__logger__.exception(exception)
            context.setError(exception)
            context.getTracking().addError(invocation)
            if crash is not None:
                if isinstance(crash, Orchestrator):
                    return cls.invoke(crash, crash.main, crash.crash, context)
                return cls.invoke(current, crash, None, context)
            else:
                message = ""
                context.setError(exception)
                if isinstance(exception, Raisable):
                    message = exception.getMessage()
                else:
                    message = str(exception)
                cls.__logger__.debug('\tCATCHED EXCEPTION: %s', message)
                context.abort(message)
                return

    def execute(self, context: StageContext):

        self.__logger__.debug('--------------- EXECUTE: %s -----------------\n'
                              '                               main: %s\n'
                              '                              crash: %s\n'
                              '                            success: %s\n'
                              '                              other: %s\n'
                              '                             follow: %s',
                              self, self.main, self.crash, self.success, self.other, self.follow)

        self.follow = Orchestrator.invoke(self, self.main, self.crash, context)

    def next(self):
        follow = self.follow
        self.follow = None
        if isinstance(follow, type):
            follow = follow()

        return follow

    @classmethod
    def of(cls, element):
        Objects.requireNonNull(element)
        return Orchestrator(element)

    def onSuccess(self, element):
        if self.success is not None:
            raise IllegalStateException('onSuccess already present')
        self.success = self.__create__(Objects.requireNonNull(element, 'onSuccess element is null'))

        return self

    def onCrash(self, element):
        if self.crash is not None:
            raise IllegalStateException('onCrash already present')
        self.crash = self.__create__(Objects.requireNonNull(element, 'onCrash element is null'))

        return self

    def orElse(self, element):
        if self.other is not None:
            raise IllegalStateException('orElse already present')
        self.other = self.__create__(Objects.requireNonNull(element, 'orElse element is null'))

        return self
