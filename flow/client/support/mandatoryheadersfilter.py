from uuid import uuid4

from piggy.base.util import Objects
from ws.rs.client.clientrequestcontext import ClientRequestContext
from ws.rs.client.clientrequestfilter import ClientRequestFilter

from plugin.config import Settings, ApiData, ApiServers, Access


class MandatoryHeadersFilter(ClientRequestFilter):

    def getRequestId(self):
        apiVersion = Settings.of(ApiData).get(ApiData.VERSION)
        deviceId = Objects.requireNonEmptyElse(Settings.of(Access).get(Access.DEVICE_ID), '0')
        return f'{Settings.of(ApiData).get(ApiData.REQUEST_ID_PREFIX)}-{apiVersion}-{deviceId}-{str(uuid4())[0:8]}'

    def filter(self, requestContext: ClientRequestContext):
        headers = requestContext.getHeaders()
        main = Settings.of(ApiServers).get(ApiServers.MAIN)
        headers.putSingle('referer', main)
        headers.putSingle('origin', main)
        headers.putSingle('x-request-id', self.getRequestId())
