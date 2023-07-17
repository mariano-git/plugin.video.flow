from uuid import uuid4

from ws.rs.client.clientrequestcontext import ClientRequestContext
from ws.rs.client.clientrequestfilter import ClientRequestFilter

from plugin.config import Settings, ApiData, ApiServers


class MandatoryHeadersFilter(ClientRequestFilter):

    def filter(self, requestContext: ClientRequestContext):
        headers = requestContext.getHeaders()
        main = Settings.of(ApiServers).get(ApiServers.MAIN)
        headers.putSingle('referer', main)
        headers.putSingle('origin', main)
        headers.putSingle('x-request-id', f'Kodi-{Settings.of(ApiData).get(ApiData.VERSION)}-{str(uuid4())}')
