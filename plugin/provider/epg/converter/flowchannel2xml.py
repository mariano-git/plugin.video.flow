
from xml.etree.ElementTree import Element, ElementTree

from flow import FlowConstants
from flow.model.content import FlowChannel
from plugin.provider.epg.converter import ImageToUrlConverter
from plugin.util import Converter


class FlowChannel2XmlConverter(Converter[FlowChannel, Element]):
    def __init__(self):
        self.imageConverter = ImageToUrlConverter(
            FlowConstants.ImageUse.CHANNEL_LOGO,
            FlowConstants.ImageSize.W350XH500
        )

    def convert(self, source: FlowChannel) -> Element:
        '''
        <channel id="channel-x">
            <display-name>Channel X</display-name>
            <display-name>Channel X HD</display-name>
            <icon src="http://path-to-icons/channel-x.png"/>
        </channel>
        '''
        xmlChannel = Element("channel", id=source.id, type=FlowConstants.ContentType.TV_CHANNEL)
        displayName = Element("display-name", lang="sp")
        displayName.text = source.title
        icon = Element("icon", src=self.imageConverter.convert(source.images))
        xmlChannel.append(displayName)
        xmlChannel.append(icon)

        return xmlChannel
