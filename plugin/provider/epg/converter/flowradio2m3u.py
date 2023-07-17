from typing import Final

from flow.model.radio import RadioStation
from plugin.config import Settings, ApiServers, Channels
from plugin.util import Converter


class FlowRadio2M3UConverter(Converter[RadioStation, str]):
    RADIO_TEMPLATE: Final[str] = '#EXTINF:-1 ' \
                                 'radio="true" ' \
                                 'tvg-id="{chId}" ' \
                                 'tvg-name="{chName}" ' \
                                 'group-title="Radio {group};{chType}",' \
                                 '{chName}\n' \
                                 '{source}'

    def __init__(self):
        self.base = Settings.of(ApiServers)
        self.group = Settings.of(Channels).get(Channels.GROUP_NAME)

    def convert(self, source: RadioStation) -> str:
        rid = source.mount if not source.mount.isnumeric() else f'RM{source.mount}'
        return self.RADIO_TEMPLATE.format(
            chId=rid,
            chName=source.name,
            chType=source.type,
            group=self.group,
            source=f'{self.base.get(ApiServers.RADIO_SRC)}/{source.mount}'
        )
