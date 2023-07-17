from typing import List

from flow.client.support import JwtAuthentication
from flow.model.content import FlowVODContent, FlowProgram, FlowChannel
from ws.rs.consumes import Consumes
from ws.rs.core.mediatype import MediaType
from ws.rs.httpmethod import GET, POST
from ws.rs.path import Path
from ws.rs.produces import Produces
from ws.rs.queryparam import QueryParam


@Path('api/v1')
class ContentApi(object):

    @GET
    @Produces({MediaType.APPLICATION_JSON})
    @Consumes({MediaType.APPLICATION_JSON})
    @Path('content/filter')
    @JwtAuthentication
    def getFilterVODContent(self, lang: QueryParam('lang'),
                            size: QueryParam('size'),
                            page: QueryParam('page'),
                            filters: QueryParam('filters'),
                            adult: QueryParam('adult') = 'false') -> FlowVODContent:
        return 'magic'

    @GET
    @Produces({MediaType.APPLICATION_JSON})
    @Consumes({MediaType.APPLICATION_JSON})
    @Path('content/filter')
    @JwtAuthentication
    def getVODContent(self, lang: QueryParam('lang'),
                            size: QueryParam('size'),
                            page: QueryParam('page'),
                            adult: QueryParam('adult') = 'false') -> FlowVODContent:
        return 'magic'

    @GET
    @Produces({MediaType.APPLICATION_JSON})
    @Consumes({MediaType.APPLICATION_JSON})
    @Path('content/serie')
    @JwtAuthentication
    def getVODSerie(self, id: QueryParam('id')) -> FlowVODContent:
        return 'magic'

    # https://web.flow.com.ar/api/v1/content?type=vod&id=39769206
    # revisar si el link de arriba responde para otro tipo de contenido
    # vod =  pelicula

    @GET
    @Produces({MediaType.APPLICATION_JSON})
    @Consumes({MediaType.APPLICATION_JSON})
    @Path('content/season')
    @JwtAuthentication
    def getVODSeason(self, id: QueryParam('id')) -> FlowVODContent:
        return 'magic'

    # Live TV
    @GET
    @Produces({MediaType.APPLICATION_JSON})
    @Consumes({MediaType.APPLICATION_JSON})
    @Path('content/channels')
    @JwtAuthentication
    def getChannels(self) -> List[FlowChannel]:
        return 'magic'

    @POST
    @Produces({MediaType.APPLICATION_JSON})
    @Consumes({MediaType.APPLICATION_JSON})
    @Path('content/channel')
    @JwtAuthentication
    def getPrograms(self, channelIds: List[int],
                    size: QueryParam('size'),
                    start: QueryParam('dateFrom'),
                    end: QueryParam('dateTo'),
                    tvRating: QueryParam('tvRating') = 6) -> List[List[FlowProgram]]:
        return 'magic'
