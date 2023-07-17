from typing import Final

from flow.model.content import FlowChannel
from plugin.config import Settings, Channels
from plugin.provider.epg.converter import ResourceToUrlConverter
from plugin.util import Converter


class FlowChannel2M3UConverter(Converter[FlowChannel, str]):
    TV_TEMPLATE: Final[str] = '#EXTINF:-1 ' \
                              'tvg-chno="{chNum}" ' \
                              'tvg-id="{chId}" ' \
                              'tvg-name="{chName}" ' \
                              'group-title="{groupName}" ' \
                              'radio="false" ' \
                              '{catchUpSrc},{chName}\n' \
                              'plugin://plugin.video.flow/play/channel/{chId}'

    def __init__(self):
        self.resourcesConverter = ResourceToUrlConverter()
        self.group = Settings.of(Channels).get(Channels.GROUP_NAME)

    def convert(self, source: FlowChannel) -> str:
        # urlDash = self.resourcesConverter.convert(source.resources)
        # urlDash = parse.quote(urlDash, safe="")
        catchUpSrc = 'catchup="vod"'

        return self.TV_TEMPLATE.format(
            chId=source.id,
            chNum=source.number,
            chName=source.title,
            # contentType=source.contentType,
            groupName=self.group,
            # source=urlDash,
            catchUpSrc=catchUpSrc
        )
