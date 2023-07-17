from flow.api.content import ContentApi
from flow.api.dynamic import DynamicApi
from flow.client import BaseClient
from flow.model.dynamic import NavPanel, DynamicAllModel
from plugin.config import Settings, Token, Base
from plugin.provider.directory.converter.flow2directory import FlowNavPanel2DirectoryConverter


class DynamicClient(BaseClient):

    def __init__(self):
        self.api = self.createResource(Settings.of(ApiServers).get(ApiServers.MAIN), DynamicApi)

    def getDynamicAll(self, deviceType:str, token:str) -> DynamicAllModel:

        return self.api.all(deviceType, token)

    def getDynamicBulk(self, uri, full):
        if not self.isJwtValid():
            self.doLogin()
        # FIXME
        if filter:
            query = f"{uri}?groupBy=series&restricted=false&showAdultContent=false&size=20"
        else:
            query = uri

        return self.dynamicApi.bulk(deviceType='Web Client', uris=query)

    def getDynamicPage(self, pageId):
        if not self.isJwtValid():
            self.doLogin()
        return self.dynamicApi.page(deviceType='Web Client', token=self.getToken(), id=pageId)






