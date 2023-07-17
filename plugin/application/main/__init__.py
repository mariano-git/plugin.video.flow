import xbmcgui
from ws.rs.httpmethod import GET
from ws.rs.path import Path
from ws.rs.queryparam import QueryParam

# FIXME
@Path('/main')
class MainEndpoint:

    @GET
    @Path('/index')
    def index(self, handler: QueryParam('handler'), resume: QueryParam):
        d = xbmcgui.Dialog()

        if d.ok(
                'ATENCION!',
                'El contenido OnDemand todavia no se encuentra disponible.\n'
                'Ingresa por TV o Radio para visualizar la programacion',

        ):
            exit(0)
