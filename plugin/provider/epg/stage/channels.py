from logging import Logger
from typing import Optional, List
from xml.etree import ElementTree as Document

from flow.client.contentclient import ContentClient
from flow.client.radioclient import RadioClient
from flow.model.content import FlowChannel
from flow.model.radio import RadioConfig
from plugin import PlugInConstants
from plugin.config import Settings, Channels, Programs
from plugin.provider.epg.converter.flowchannel2m3u import FlowChannel2M3UConverter
from plugin.provider.epg.converter.flowchannel2xml import FlowChannel2XmlConverter
from plugin.provider.epg.converter.flowradio2m3u import FlowRadio2M3UConverter
from plugin.provider.epg.converter.flowradio2xml import FlowRadio2XmlConverter
from plugin.provider.epg.stage import BaseRetriever
from plugin.stage import StageContext

from plugin.util import ProgressIndicator


class ChannelsRetriever(BaseRetriever):

    def isValid(self, channel: FlowChannel, logger: Logger):
        if channel.resources is None:
            logger.warning('Channel: "%s" - "%s" - "%s", doesn\'t contain resources',
                           channel.title, channel.id, channel.number
                           )
            return False
        for resource in channel.resources:
            if resource.protocol in PlugInConstants.STREAMING_PROTOCOLS and \
                    resource.encryption in PlugInConstants.STREAMING_ENCRYPTIONS:
                return True
        logger.warning('Channel: "%s" - "%s" - "%s", doesn\'t contain a compatible resource',
                       channel.title, channel.id, channel.number
                       )
        return False

    def retrieve(self, context: StageContext, settings: Channels):
        # Display Load Dialog
        progress: ProgressIndicator
        if settings.isEnabled(Channels.SHOW_PROGRESS):
            progress = ProgressIndicator.of(100, 'Cargando...', 'Cargando Canales desde Flow')
        else:
            progress = ProgressIndicator.ofNull()

        tvClient: ContentClient = context.getComponent(ContentClient)
        radioClient: RadioClient = context.getComponent(RadioClient)

        channels: List[FlowChannel] = tvClient.getChannels()
        progress.update(50, 'Cargando Radios desde Flow')

        radioConfig: RadioConfig = radioClient.getConfig()
        progress.update(100, 'Carga finalizada')

        xmlRoot = Document.Element('tv')
        flowChannel2xml = FlowChannel2XmlConverter()
        flowChannel2m3u = FlowChannel2M3UConverter()
        m3u: List[str] = list()

        m3u.append('#EXTM3U tvg-shift=0')

        logger: Logger = context.getLogger(self)
        for channel in channels:
            if self.isValid(channel, logger):
                xmlRoot.append(flowChannel2xml.convert(channel))
                m3u.append(flowChannel2m3u.convert(channel))

        del channels

        flowRadio2xml = FlowRadio2XmlConverter()
        flowRadio2m3u = FlowRadio2M3UConverter()
        for station in radioConfig.config.radios:
            xmlRoot.append(flowRadio2xml.convert(station))
            m3u.append(flowRadio2m3u.convert(station))

        del radioConfig

        self.saveChannelsEpg(logger, progress, Document.ElementTree(xmlRoot), m3u)

        settings.setLast()
        Settings.of(Programs).setLast(0)
        return True

    def channels(self, context: StageContext, settings: Channels):
        channels = self.getChannels()
        if channels is not None:
            return True

        return self.retrieve(
            context, settings
        )

    def execute(self, context: StageContext) -> Optional[bool]:
        settings: Channels = Settings.of(Channels)
        if settings.isCurrent():
            return self.channels(context, settings)
        return self.retrieve(
            context, settings
        )
