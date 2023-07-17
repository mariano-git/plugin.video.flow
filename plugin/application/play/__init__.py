from typing import Optional, cast

import xbmcgui
import xbmcplugin
from piggy.base.util.logging import Logger
from ws.rs.httpmethod import GET
from ws.rs.path import Path
from ws.rs.pathparam import PathParam
from ws.rs.queryparam import QueryParam

from flow import FlowConstants
from flow.client.prmclient import PrmClient
from flow.model.prm import ContentSourceResponse
from plugin.application.play.drmheadersbuilder import DRMHeadersBuilder
from plugin.config import Settings, PRM, JWT, Access, ApiServers
from plugin.stage import StageContext, Stage
from plugin.stage.orchestrator import Orchestrator
from plugin.stage.stageexecutor import StageExecutor


class ContentSourceGetter(Stage):
    def execute(self, context: StageContext) -> Optional[bool]:
        client: PrmClient = context.getComponent(PrmClient)
        sourceId = context.getParam('id')
        sourceType = context.getParam('sourceType')
        drmId = Settings.of(Access).get(Access.VUID)
        response: ContentSourceResponse = client.contentSource(
            sourceId, sourceType, drmId
        )
        context.setProperty('content', response)
        return True


class PrmRegistration(Stage):
    def execute(self, context: StageContext) -> Optional[bool]:
        prmSettings = Settings.of(PRM)
        if not prmSettings.isCurrent():
            client: PrmClient = context.getComponent(PrmClient)
            result = client.registerForPrm()
            prmSettings.set(PRM.VALUE, result.tokenForPRM)
            prmSettings.setLast()
        return True


class PrepareLicAndPlay(Stage):
    __logger__ = Logger.getLogger(f'{__name__}.{__qualname__}')

    def execute(self, context: StageContext) -> Optional[bool]:
        content: ContentSourceResponse = cast(ContentSourceResponse, context.getProperty('content'))
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

        xbmcplugin.setResolvedUrl(context.getParam('handler'), True, listitem=player)
        return True


class ShowMissingMessage(Stage):
    def execute(self, context: StageContext) -> Optional[bool]:
        d = xbmcgui.Dialog()
        msg = "El contenido seleccionado ya no se encuentra disponible"
        d.ok("No Encontrado...", msg)
        context.abort('Prm Negotiation Failed')


class End(Stage):
    def execute(self, context: StageContext) -> Optional[bool]:
        context.abort('End OK')


@Path('/play')
class PlayEndpoint:
    main: Orchestrator = Orchestrator.of(PrmRegistration).onSuccess(
        Orchestrator.of(ContentSourceGetter).onSuccess(
            Orchestrator.of(PrepareLicAndPlay).onSuccess(End)
        )
    ).onCrash(ShowMissingMessage)

    EXECUTOR: StageExecutor = StageExecutor().configure(main)

    @GET
    @Path('/channel/{id}')
    def playChannel(self, handler: QueryParam('handler'), channelId: PathParam('id'), resume: QueryParam):
        # FIXME handler should be int
        self.EXECUTOR.contextParam('handler', int(handler)).contextParam(
            'sourceType', FlowConstants.ContentType.TV_CHANNEL
        ).contextParam('id', channelId).execute()

    @GET
    @Path('/program/{id}')
    def playProgram(self, handler: QueryParam('handler'), programId: PathParam('id'), resume: QueryParam):
        # FIXME handler should be int
        self.EXECUTOR.contextParam('handler', int(handler)).contextParam(
            'sourceType', FlowConstants.ContentType.TV_SCHEDULE
        ).contextParam('id', programId).execute()
