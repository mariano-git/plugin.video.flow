from xml.etree import ElementTree as Document

from piggy.mapper.documentmapper import DocumentMapper

from plugin.config import Epg, Programs, Settings
from plugin.provider.epg.model.xmltv import XmlTvChannels
from plugin.stage import Stage, StageContext
from plugin.util import ProgressIndicator, File


class TVScheduleCurrent(Stage):
    def execute(self, context: StageContext):
        if Settings.of(Programs).isTVScheduleCurrent():
            context.wait(Stage.LONG_WAIT)
            return True
        else:
            return False


class BaseRetriever(Stage):

    def getChannels(self):
        settings = Settings.of(Epg)
        file = File.of(settings.get(Epg.PATH), settings.get(Epg.XML_EPG_FILE))
        if file.exists():
            om = DocumentMapper()
            return om.readDocument(file.toString(), XmlTvChannels)
        return None

    def saveProgramsEpg(self, logger, programs):
        settings = Settings.of(Epg)
        encoding = 'utf-8'
        fileName = File.of(settings.get(Epg.PATH), settings.get(Epg.XML_EPG_FILE)).toString()
        document = Document.parse(fileName)
        root = document.getroot()
        programmes = root.findall('programme')
        for p in programmes: root.remove(p)
        for p in programs: root.append(p)
        logger.info(
            f"\n \
                                                   ********************************************\n \
                                                   Saving xml channels: \"{fileName}\" \n \
                                                   ********************************************")
        with open(fileName, "wb") as xmlFile:
            document.write(xmlFile, encoding, True)
            xmlFile.close()

    def saveChannelsEpg(self, logger, progress: ProgressIndicator, document, m3u):
        settings = Settings.of(Epg)
        encoding = 'utf-8'

        file = File.of(settings.get(Epg.PATH))

        xmlFileName = file.append(settings.get(Epg.XML_EPG_FILE)).toString()
        m3uFileName = file.append(settings.get(Epg.M3U_EPG_FILE)).toString()

        logger.info(
            f"\n \
                                           ********************************************\n \
                                           Saving m3u channels: \"{m3uFileName}\" \n \
                                           Saving xml channels: \"{xmlFileName}\" \n \
                                           ********************************************")
        with open(xmlFileName, "wb") as xmlFile:
            document.write(xmlFile, encoding, xml_declaration=True, short_empty_elements=True)
            xmlFile.close()
        progress.refresh(3)

        with open(m3uFileName, "w", encoding=encoding) as m3uFile:
            for item in m3u:
                m3uFile.write(f'{item}\n')
            m3uFile.close()
        progress.refresh(3)
        progress.done()
