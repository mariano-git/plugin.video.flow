import xbmc

from plugin.provider.auth.stage import DestroyUserData, EvaluateJwtExpiration, DoLogin, CallDevice, IsJWTValid
from plugin.provider.boot.stage import Resume, CheckConfig, DisplayConfigurationMessage
from plugin.provider.directory.stage.directory import CheckDirectory
from plugin.provider.epg.stage import TVScheduleCurrent
from plugin.provider.epg.stage.channels import ChannelsRetriever
from plugin.provider.epg.stage.programs import ProgramsRetriever

from plugin.service.executor import ServiceExecutor
# from plugin.service.stage.bootstage import CheckConfig, DisplayConfigurationMessage, IsJWTValid, CallDevice, DoLogin, \
#    DestroyUserData, DestroyTokens, EvaluateJwtExpiration, Resume

from plugin.stage.orchestrator import Orchestrator


class Service:
    def __init__(self):
        self.executor = ServiceExecutor()

    def configure(self):
        wipeData = Orchestrator.of(DestroyUserData)

        # checkVOD = Orchestrator.of(CheckVOD)

        checkDirectory = Orchestrator.of(CheckDirectory)

        resume = Orchestrator.of(Resume).onSuccess(Resume)

        evaluateJwtExpiration = Orchestrator.of(EvaluateJwtExpiration).onSuccess(
            Orchestrator.of(DoLogin).onSuccess(resume).orElse(wipeData)
        )

        # evaluateJwtExpiration = Orchestrator.of(EvaluateJwtExpiration).onSuccess(DoLogin).onCrash(wipeData)

        login = Orchestrator.of(DoLogin).onCrash(wipeData)

        checkEpg = Orchestrator.of(TVScheduleCurrent).onSuccess(checkDirectory).orElse(
            Orchestrator.of(CallDevice).onSuccess(
                Orchestrator.of(ChannelsRetriever).onSuccess(
                    Orchestrator.of(ProgramsRetriever).onCrash(evaluateJwtExpiration)
                ).onCrash(evaluateJwtExpiration)
            ).orElse(login).onCrash(login)
        )

        login.onSuccess(checkEpg)

        authorization = Orchestrator.of(IsJWTValid).onSuccess(
            checkEpg
        ).orElse(login)

        # checkVOD.orElse(authorization)

        start = Orchestrator.of(CheckConfig).onCrash(DisplayConfigurationMessage).onSuccess(authorization)

        wipeData.onSuccess(start)

        self.executor.observes(xbmc.Monitor()).configure(start)

    def getExecutor(self):
        return self.executor


