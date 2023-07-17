from flow.model.radio import RadioStations, RadioConfig, RadioPrograms
from plugin.config import Settings, ApiServers

from ws.rs.core.mediatype import MediaType
from ws.rs.httpmethod import GET
from ws.rs.path import Path
from ws.rs.produces import Produces
from ws.rs.queryparam import QueryParam


class RadioApi:
    @GET
    @Path(f'{Settings.of(ApiServers).get(ApiServers.RADIO_SRC)}/ws/stations')
    @Produces(MediaType.APPLICATION_JSON)
    def getStations(self) -> RadioStations:
        pass

    @GET
    @Path(f'{Settings.of(ApiServers).get(ApiServers.APP)}/contextual/musicapp/config/es-AR.json')
    @Produces(MediaType.APPLICATION_JSON)
    def getRadioConfig(self) -> RadioConfig:
        pass

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    @Path(f'{Settings.of(ApiServers).get(ApiServers.RADIO_APP)}/api/cienradios/v2/GetProgramasActualesDeRadios')
    def getPrograms(self, idsRadios: QueryParam('idsRadios'),
                    cantidadProgramas: QueryParam('cantidadProgramas')) -> RadioPrograms:
        pass
