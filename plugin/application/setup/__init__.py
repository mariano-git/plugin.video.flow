import xbmcaddon
import xbmcgui
from ws.rs.httpmethod import GET
from ws.rs.path import Path
from ws.rs.queryparam import QueryParam

from plugin import PlugInConstants
from plugin.config import Settings, Epg
from plugin.util import File


@Path('/setup')
class SetupEndpoint:

    def setUpIptvSimple(self):
        settings = Settings.of(Epg)
        file = File.of(settings.get(Epg.PATH))
        xmlFileName = file.append(settings.get(Epg.XML_EPG_FILE)).toString()
        m3uFileName = file.append(settings.get(Epg.M3U_EPG_FILE)).toString()
        iptvSettings = xbmcaddon.Addon(PlugInConstants.IPTV_SIMPLE_PLUGIN)
        iptvSettings.setSettingInt("m3uPathType", 0)
        iptvSettings.setSetting("m3uPath", m3uFileName)
        iptvSettings.setSettingInt("epgPathType", 0)
        iptvSettings.setSetting("epgPath", xmlFileName)
        iptvSettings.setSettingBool("epgCache", False)
        iptvSettings.setSettingInt("logoFromEpg", 2)
        iptvSettings.setSettingBool("timeshiftEnabled", True)
        iptvSettings.setSettingBool("catchupEnabled", True)
        iptvSettings.setSettingBool("catchupPlayEpgAsLive", True)

    @GET
    @Path('/pvr')
    def setupPVR(self, handler: QueryParam('handler'), resume: QueryParam):
        d = xbmcgui.Dialog()

        if d.yesno(
                'ATENCION!',
                'Estas por cambiar la configuracion de IPTV Simple.',
                'Cancelar',
                'Continuar'
        ):
            self.setUpIptvSimple()
            d.ok("Hecho!", 'Configuracion Realizada')
