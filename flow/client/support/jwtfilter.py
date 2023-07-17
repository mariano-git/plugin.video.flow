from flow.client.support import JwtAuthentication


from plugin.config import Settings, JWT
from ws.rs.client.clientrequestcontext import ClientRequestContext
from ws.rs.client.clientrequestfilter import ClientRequestFilter
from ws.rs.core.httpheaders import HttpHeaders
from ws.rs.core.response import Response


@JwtAuthentication
class JWTAuthFilter(ClientRequestFilter):

    def filter(self, requestContext: ClientRequestContext):

        jwt = Settings.of(JWT)

        if not jwt.isCurrent():
            requestContext.abortWith(
                Response.status(Response.Status.PRECONDITION_FAILED).entity(
                    "Filter detected an invalid or expired jwt token"
                ).build()
            )
        else:
            token: str = jwt.get(JWT.VALUE)
            if token:
                requestContext.getHeaders().putSingle(HttpHeaders.AUTHORIZATION, f'Bearer {token}')
