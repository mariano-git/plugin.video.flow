from flow.client.support import JwtAuthentication, PrmAuthentication
from flow.model.prm import *
from ws.rs.consumes import Consumes
from ws.rs.core.mediatype import MediaType
from ws.rs.httpmethod import POST, GET
from ws.rs.path import Path
from ws.rs.produces import Produces
from ws.rs.queryparam import QueryParam


@Path('prm/v1')
class PrmApi:
    @POST
    @Path('concurrency')
    @Consumes({MediaType.APPLICATION_JSON})
    @Produces({MediaType.APPLICATION_JSON})
    @JwtAuthentication
    def concurrency(self, concurrencyPayload: ConcurrencyRequest) -> ConcurrencyResponse:
        pass

    @GET
    @Path('contentSource')
    @Produces({MediaType.APPLICATION_JSON})
    @PrmAuthentication
    def contentSource(self, sourceId: QueryParam('id'),
                      sourceType: QueryParam('type'), drmId: QueryParam('drmId')) -> ContentSourceResponse:
        pass

    @POST
    @Path('register')
    @Consumes({MediaType.APPLICATION_JSON})
    @Produces({MediaType.APPLICATION_JSON})
    @JwtAuthentication
    def register(self, registerPayload: RegisterRequest) -> RegisterResponse:
        pass
