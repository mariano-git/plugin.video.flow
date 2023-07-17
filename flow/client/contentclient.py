from typing import List

from flow.api.content import ContentApi
from flow.client import BaseClient
from flow.model.content import FlowChannel, FlowProgram, FlowVODContent
from plugin.config import Settings, ApiServers


class ContentClient(BaseClient):

    def getChannels(self) -> List[FlowChannel]:
        api: ContentApi = self.createResource(Settings.of(ApiServers).get(ApiServers.MAIN), ContentApi)

        channelList: List[FlowChannel] = api.getChannels()
        return channelList

    def getPrograms(self, channelIds: List[int], size: int, start: int, end: int, tvRating: int) -> List[
        List[FlowProgram]]:
        api: ContentApi = self.createResource(Settings.of(ApiServers).get(ApiServers.MAIN), ContentApi)

        programList: List[List[FlowProgram]] = api.getPrograms(channelIds, size, start, end, tvRating)
        return programList

    def getFilterVODContent(self, size, page, filters, lang='es') -> FlowVODContent:
        api: ContentApi = self.createResource(Settings.of(ApiServers).get(ApiServers.MAIN), ContentApi)
        content: FlowVODContent = api.getFilterVODContent(lang, size, page, filters)
        return content

    def getVODContent(self, size, page, lang='es') -> FlowVODContent:
        api: ContentApi = self.createResource(Settings.of(ApiServers).get(ApiServers.MAIN), ContentApi)
        content: FlowVODContent = api.getVODContent(lang, size, page)
        return content
