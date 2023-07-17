from flow.api.prm import PrmApi
from flow.client import BaseClient
from flow.model.prm import RegisterRequest

from plugin.config import Settings, ApiServers, ApiData


class PrmClient(BaseClient):
    def contentSource(self, sourceId: str, sourceType: str, drmId: str):
        api: PrmApi = self.createResource(Settings.of(ApiServers).get(ApiServers.MAIN), PrmApi)
        return api.contentSource(sourceId=sourceId, sourceType=sourceType, drmId=drmId)

    def registerForPrm(self):
        api: PrmApi = self.createResource(Settings.of(ApiServers).get(ApiServers.MAIN), PrmApi)
        settings = Settings.of(ApiData)
        prmRequest: RegisterRequest = RegisterRequest()
        prmRequest.deviceBrand = ""
        prmRequest.deviceModel = ""
        prmRequest.deviceType = settings.get(ApiData.DEVICE_TYPE)
        prmRequest.playerType = settings.get(ApiData.PLAYER)
        prmRequest.networkType = settings.get(ApiData.NETWORK)

        return api.register(prmRequest)
