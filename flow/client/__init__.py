from typing import Type, TypeVar

from flow.client.support.jwtfilter import JWTAuthFilter
from flow.client.support.mandatoryheadersfilter import MandatoryHeadersFilter
from flow.client.support.prmfilter import PRMAuthFilter
from piggy.base.util.concurrent.timeunit import TimeUnit
from piggy.restful.client.clientresourcefactory import ClientResourceFactory
from piggy.restful.client.clientsetup import ClientSetup
from piggy.restful.ext.spi.json.jsonfeature import JsonFeature
from ws.rs.client.client import Client
from ws.rs.client.clientbuilder import ClientBuilder
from ws.rs.client.webtarget import WebTarget
from ws.rs.core.configuration import Configuration

T = TypeVar('T')


class BaseClient:

    def getConfigurable(self):
        config: ClientSetup = ClientSetup()
        config.register(JsonFeature)
        config.register(JWTAuthFilter)
        config.register(PRMAuthFilter)
        config.register(MandatoryHeadersFilter)
        return config

    def createClient(self):
        config: Configuration = self.getConfigurable().getConfiguration()
        return ClientBuilder.newBuilder() \
            .withConfig(config) \
            .connectTimeout(5, TimeUnit.SECONDS) \
            .readTimeout(4, TimeUnit.SECONDS) \
            .build()

    def createTarget(self, baseUrl: str) -> WebTarget:
        client: Client = self.createClient()
        webTarget: WebTarget = client.target(baseUrl)
        return webTarget

    def createResource(self, baseUrl: str, theApi: Type[T]) -> T:
        target = self.createTarget(baseUrl)
        return ClientResourceFactory.newResource(theApi, target)
