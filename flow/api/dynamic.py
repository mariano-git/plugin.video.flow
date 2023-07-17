from typing import List

from flow.client.support import JwtAuthentication
from flow.model.dynamic import DynamicAllModel, DynamicBulkModel
from ws.rs.consumes import Consumes
from ws.rs.core.mediatype import MediaType
from ws.rs.httpmethod import GET
from ws.rs.path import Path
from ws.rs.produces import Produces
from ws.rs.queryparam import QueryParam


@Path('api/v1')
class DynamicApi(object):

    @GET
    @Path("dynamic/all")
    @Produces({MediaType.APPLICATION_JSON})
    @Consumes({MediaType.APPLICATION_JSON})
    @JwtAuthentication
    def all(self, deviceType: QueryParam('deviceType'), token: QueryParam('token')) -> DynamicAllModel:
        return 'magic'

    @GET
    @Path("dynamic/page")
    @Produces({MediaType.APPLICATION_JSON})
    @Consumes({MediaType.APPLICATION_JSON})
    @JwtAuthentication
    def page(self, deviceType: QueryParam('deviceType'), token: QueryParam('token'),
             pageId: QueryParam('id')) -> DynamicAllModel:
        return 'magic'

    @GET
    @Path("dynamic/bulk")
    @Produces({MediaType.APPLICATION_JSON})
    @Consumes({MediaType.APPLICATION_JSON})
    @JwtAuthentication
    def bulk(self, deviceType: QueryParam('deviceType'), uris: QueryParam('uris')) -> List[DynamicBulkModel]:
        return 'magic'
