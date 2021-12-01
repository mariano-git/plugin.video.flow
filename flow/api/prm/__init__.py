from ext.util import ModelHelper
from ext.ws.rs import Path, POST, Consumes, Produces, QueryParam, GET
from ext.ws.rs.core import MediaType


class ConcurrencyRequest(ModelHelper):
    status: str  # "PLAY",
    playbackSessionId: str
    playbackResourceId: str


class ConcurrencyResponse(ModelHelper):
    pass


class ContentSourceResponse(ModelHelper):
    pass


class RegisterRequest(ModelHelper):
    deviceBrand: str  # ""
    deviceModel: str  # ""
    deviceType: str  # "WEB","
    playerType: str  # "VISUAL_ON",
    networkType: str  # "BROADBAND"}'
    # TODO Move this to configuration


class RegisterResponse(ModelHelper):
    pass


@Path('prm/v1')
class PrmApi:
    @POST
    @Path('concurrency')
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    def concurrency(self, concurrencyPayload: ConcurrencyRequest) -> ConcurrencyResponse:
        pass

    @GET
    @Path('contentSource')
    @Produces(MediaType.APPLICATION_JSON)
    def contentSource(self, sourceId: QueryParam(name='id'),
                      sourceType: QueryParam(name='type')) -> ContentSourceResponse:
        pass

    @POST
    @Path('register')
    @Produces(MediaType.APPLICATION_JSON)
    def register(self, registerPayload: RegisterRequest) -> RegisterResponse:
        pass
