from flow.client.support import PrmAuthentication
from plugin.config import Settings, PRM
from ws.rs.client.clientrequestcontext import ClientRequestContext
from ws.rs.client.clientrequestfilter import ClientRequestFilter
from ws.rs.core.httpheaders import HttpHeaders
from ws.rs.core.response import Response


@PrmAuthentication
class PRMAuthFilter(ClientRequestFilter):

    def filter(self, requestContext: ClientRequestContext):

        prm = Settings.of(PRM)

        if not prm.isCurrent():
            requestContext.abortWith(
                Response.status(Response.Status.PRECONDITION_FAILED).entity(
                    "Filter detected an invalid or expired prm token"
                ).build()
            )
        else:
            token: str = prm.get(PRM.VALUE)
            if token:
                requestContext.getHeaders().putSingle(HttpHeaders.AUTHORIZATION, f'Bearer {token}')
