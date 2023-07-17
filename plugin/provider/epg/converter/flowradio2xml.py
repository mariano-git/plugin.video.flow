from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from flow import FlowConstants
from flow.model.radio import RadioStation
from plugin.config import Settings, ApiServers
from plugin.util import Converter


class FlowRadio2XmlConverter(Converter[RadioStation, Element]):
    def __init__(self):
        self.base = Settings.of(ApiServers)

    def convert(self, source: RadioStation) -> Element:
        rid = source.mount if not source.mount.isnumeric() else f'RM{source.mount}'
        xmlRadio = ElementTree.Element("channel", id=rid, type=FlowConstants.ContentType.RADIO_STATION)
        ElementTree.SubElement(xmlRadio, "display-name", lang="sp").text = source.name
        ElementTree.SubElement(xmlRadio, "icon", src=f'{self.base.get(ApiServers.RADIO_IMG)}/{source.logo}')
        return xmlRadio
