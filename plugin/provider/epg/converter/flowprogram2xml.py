from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from flow import FlowConstants
from flow.model.content import FlowProgram
from piggy.base.util import Objects
from piggy.base.util.date import Date
from piggy.base.util.simpledateformat import SimpleDateFormat
from plugin.provider.epg.converter import ImageToUrlConverter
from plugin.util import Converter


class FlowProgram2XmlConverter(Converter[FlowProgram, Element]):
    CATCHUP_URI = "plugin://plugin.video.flow/play/program/{sourceId}"
    DATE_FORMAT = SimpleDateFormat('%Y%m%d%H%M%S %z')

    def __init__(self):
        self.imageConverter = ImageToUrlConverter(
            FlowConstants.ImageUse.DESCRIPTION,
            FlowConstants.ImageSize.W350XH500
        )

    def setCategory(self, element, genre):
        if not Objects.isEmpty(genre):
            genre = genre.split(',')
            for g in genre:
                ElementTree.SubElement(element, "category", lang="sp").text = g

    def setSeason(self, element, episode, season):
        if not Objects.isEmpty(episode) and not Objects.isEmpty(season):
            season = season if season > 10 else f'0{season}'
            episode = episode if episode > 10 else f'0{episode}'
            ElementTree.SubElement(element, 'episode-num', {'system': 'onscreen'}).text = f'S{season}E{episode}'

    def convert(self, source: FlowProgram) -> Element:
        '''
        <programme start="20080715003000 -0600" stop="20080715010000 -0600" channel="channel-x" catchup-id="34534590">
            <title>My Show</title>
            <desc>Description of My Show</desc>
            <category>Drama</category>
            <category>Mystery</category>
            <sub-title>Episode name for My Show</sub-title>
            <date>20080711</date>
            <star-rating>
              <value>6/10</value>
            </star-rating>
            <episode-num system="xmltv_ns">0.1.0/1</episode-num>
            <episode-num system="onscreen">S01E02</episode-num>
            <credits>
              <director>Director One</director>
              <writer>Writer One</writer>
              <actor>Actor One</actor>
            </credits>
            <icon src="http://path-to-icons/my-show.png"/>
        </programme>
        '''
        catchUpUri = self.CATCHUP_URI.format(sourceId=source.id)
        logo = self.imageConverter.convert(source.images)

        xmlProg = ElementTree.Element("programme",
                                      start=self.DATE_FORMAT.format(Date(source.startTime)),
                                      stop=self.DATE_FORMAT.format(Date(source.endTime)),
                                      channel=source.channelId,
                                      id=source.id
                                      )
        xmlProg.set('catchup-id', catchUpUri)
        ElementTree.SubElement(xmlProg, "title", lang="sp").text = source.title
        ElementTree.SubElement(xmlProg, "desc", lang="sp").text = source.description if not Objects.isEmpty(
            source.description) else source.title
        self.setCategory(xmlProg, source.genre)
        self.setSeason(xmlProg, source.seasonNumber, source.episodeNumber)
        ElementTree.SubElement(xmlProg, "icon", src=logo)

        return xmlProg
