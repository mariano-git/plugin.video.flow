from flow.api.prm import PrmApi
from flow.client import BaseClient
from flow.model.prm import RegisterRequest

from plugin.config import Settings, ApiServers, ApiData


class PrmClient(BaseClient):

    def __init__(self):
        self.api = self.createResource(Settings.of(ApiServers).get(ApiServers.MAIN), PrmApi)

    def contentSource(self, sourceId: str, sourceType: str, drmId: str):
        return self.api.contentSource(sourceId=sourceId, sourceType=sourceType, drmId=drmId)

    def registerForPrm(self):
        api: PrmApi = self.createResource(Settings.of(ApiServers).get(ApiServers.MAIN), PrmApi)
        settings = Settings.of(ApiData)
        prmRequest: RegisterRequest = RegisterRequest()
        prmRequest.deviceBrand = ""
        prmRequest.deviceModel = ""
        prmRequest.deviceType = settings.get(ApiData.DEVICE_TYPE)
        prmRequest.playerType = settings.get(ApiData.PLAYER)
        prmRequest.networkType = settings.get(ApiData.NETWORK)

        return self.api.register(prmRequest)
