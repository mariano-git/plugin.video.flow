import xbmc

from ext.util.logger import Logger
from flow.client.flow_client import ApiDriver

apiDriver: ApiDriver = ApiDriver()


class Step:
    def __init__(self):
        self.seconds = 1
        self.context = {}
        self.true = None
        self.false = None

    def onTrue(self, step):
        self.true = step

    def onFalse(self, step):
        self.false = step

    def wait(self):
        return self.seconds


class CheckEpg(Step):
    def invoke(self):
        isValid = apiDriver.isEpgTime()
        if isValid:
            return self.true
        return self.false


class GetChannels(Step):
    def invoke(self):
        ret = apiDriver.getChannels()
        if ret:
            return self.true
        return self.false


class GetPrograms(Step):
    def invoke(self):
        ret = apiDriver.getPrograms()
        if ret:
            return self.true
        return self.false


class BuildEpg(Step):
    def invoke(self):
        isValid = apiDriver.buildFullEpg()
        if isValid:
            return self.true
        return self.false


class CheckConfig(Step):
    def invoke(self):
        isValid = apiDriver.isReady()
        if isValid:
            return self.true
        return self.false


class CheckJwt(Step):
    def invoke(self):
        isValid = apiDriver.isJwtValid()
        if isValid:
            return self.true
        return self.false


class Login(Step):
    def invoke(self):
        isValid = apiDriver.doLogin()
        if isValid:
            return self.true
        return self.false


class Sleep(Step):
    def __init__(self):
        super().__init__()
        self._pause = 1
        self.then = None
        self.called = False

    def pause(self, seconds):
        self._pause = seconds
        return self

    def wait(self):
        if not self.called:
            return self.seconds
        return self._pause

    def andThen(self, step):
        self.then = step
        return self

    def invoke(self):
        if not self.called:
            self.called = True
            return self
        else:
            self.called = False
        return self.then


doCheckConfig: CheckConfig = CheckConfig()
doCheckJwt: CheckJwt = CheckJwt()
doCheckEpg: CheckEpg = CheckEpg()
doPullChannels: GetChannels = GetChannels()
doPullPrograms: GetPrograms = GetPrograms()
doBuildEpg: BuildEpg = BuildEpg()

doLogin: Login = Login()
doSleep: Sleep = Sleep()

doBuildEpg.onTrue(Sleep().pause(5).andThen(doCheckJwt))

doPullPrograms.onTrue(doPullPrograms)
doPullPrograms.onFalse(doBuildEpg)

doPullChannels.onTrue(doPullPrograms)
# doPullChannels.onFalse(doBuildEpg)

doCheckEpg.onTrue(doPullChannels)
doCheckEpg.onFalse(Sleep().pause(5).andThen(doCheckJwt))

doCheckJwt.onTrue(doCheckEpg)
doCheckJwt.onFalse(doLogin)

doCheckConfig.onTrue(doCheckJwt)
doCheckConfig.onFalse(Sleep().pause(5).andThen(doCheckConfig))

doLogin.onTrue(doCheckEpg)
doLogin.onFalse(doCheckConfig)

currentStep = doCheckConfig

if __name__ == "__main__":
    Logger.log("Starting Service...")

    monitor = xbmc.Monitor()

    while not monitor.abortRequested():
        currentStep = currentStep.invoke()
        if monitor.waitForAbort(currentStep.wait()):
            Logger.log("Exiting Service...")
            break
    exit(0)
