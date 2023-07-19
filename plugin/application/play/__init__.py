import xbmcgui
import xbmcplugin
from piggy.base.util.logging import Logger
from ws.rs.httpmethod import GET
from ws.rs.path import Path
from ws.rs.pathparam import PathParam
from ws.rs.queryparam import QueryParam
from ws.rs.webapplicationexception import WebApplicationException

from flow import FlowConstants
from flow.client.prmclient import PrmClient
from flow.model.prm import ContentSourceResponse
from plugin.application.play.drmheadersbuilder import DRMHeadersBuilder
from plugin.config import Settings, PRM, Access, ApiServers, JWT


@Path('/play')
class PlayEndpoint:
    def checkPrmRegistration(self, client: PrmClient):
        prmSettings = Settings.of(PRM)
        if not prmSettings.isCurrent():
            result = client.registerForPrm()
            prmSettings.set(PRM.VALUE, result.tokenForPRM)
            prmSettings.setLast()

    def getContentSource(self, client, sourceId, sourceType):
        try:
            drmId = Settings.of(Access).get(Access.VUID)
            response: ContentSourceResponse = client.contentSource(
                sourceId, sourceType, drmId
            )
            return response
        except WebApplicationException as e:
            __logger__ = Logger.getLogger(f'{self.__class__.__name__}.{self.__class__.__qualname__}')
            __logger__.exception('Unable to play ', e)
            return None

    def play(self, handler, contenType, id):
        client: PrmClient = PrmClient()
        self.checkPrmRegistration(client)
        content: ContentSourceResponse = self.getContentSource(client, id, contenType)

        if content is None:
            d = xbmcgui.Dialog()
            msg = "El contenido seleccionado ya no se encuentra disponible"
            d.ok("No Encontrado...", msg)
            return

        origin = Settings.of(ApiServers).get(ApiServers.APP)
        headers = DRMHeadersBuilder.builder().withJwt(
            # FIXME: Weird shit happens if don't replace. Base64 should be allowed...
            Settings.of(JWT).get(JWT.VALUE).replace('+', '%2B').replace('/', '%2F')
        ).withToken(
            # FIXME: Weird shit happens if don't replace. Base64 should be allowed...
            content.drm.token.replace('+', '%2B').replace('/', '%2F')
        ).withAccept('*/*').withContentType(
            'application/octet-stream'
        ).withReferer(origin).withOrigin(origin).build()

        widevineLic = [content.drm.url, headers, 'R{SSM}|']
        licenseKey = '|'.join(widevineLic)

        player = xbmcgui.ListItem(path=content.contentUrl.replace('http', 'https'))
        player.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
        player.setProperty('inputstream.adaptive.license_key', licenseKey)
        player.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        player.setProperty('inputstream', 'inputstream.adaptive')
        player.setMimeType('application/dash+xml')
        player.setContentLookup(False)

        xbmcplugin.setResolvedUrl(handler, True, listitem=player)

    @GET
    @Path('/channel/{id}')
    def playChannel(self, handler: QueryParam('handler'), channelId: PathParam('id'), resume: QueryParam):
        self.play(int(handler), FlowConstants.ContentType.TV_CHANNEL, channelId)

    @GET
    @Path('/program/{id}')
    def playProgram(self, handler: QueryParam('handler'), programId: PathParam('id'), resume: QueryParam):
        self.play(int(handler), FlowConstants.ContentType.TV_SCHEDULE, programId)
