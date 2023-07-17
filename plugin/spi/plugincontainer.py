from typing import Type

from piggy.base.io.inputstream import InputStream
from piggy.base.net.uri import URI
from piggy.base.util import Objects
from piggy.base.util.logging import Logger
from piggy.restful.internal.mappropertiesdelegate import MapPropertiesDelegate
from piggy.restful.internal.server.applicationhandler import ApplicationHandler
from piggy.restful.internal.server.containerrequest import ContainerRequest
from piggy.restful.internal.server.spi import Container
from ws.rs.core.application import Application
from ws.rs.core.uribuilder import UriBuilder


class PlugInContainer(Container):
    __lg__ = Logger.getLogger(f'{__name__}.{__qualname__}')

    def __init__(self, application: Type[Application]):
        self.applicationHandler = ApplicationHandler(application)

    @classmethod
    def create(cls, application: Type[Application]):
        return PlugInContainer(application)

    def start(self):
        # TODO: Reserved for future configuration or thread start
        return self

    def getBaseUri(self, args):
        return URI.create(args[0])

    def getRequestUri(self, args):
        resume = None
        handler = None
        uriBuilder: UriBuilder = None
        for arg in args:
            if Objects.isEmpty(arg):
                continue
            if arg.startswith('plugin'):
                uriBuilder = UriBuilder.fromUri(arg)
            elif arg.startswith('resume'):
                resume = arg.split(':')
            else:
                handler = arg
        if handler:
            uriBuilder.queryParam('handler', handler)
        else:
            uriBuilder.queryParam('handler', -1)
        if resume:
            uriBuilder.queryParam(resume[0], resume[1])
        return uriBuilder.build()

    def service(self, args):
        self.__lg__.debug('Service: %s', args)
        baseUri = self.getBaseUri(args)
        requestUri = self.getRequestUri(args)
        request = ContainerRequest(
            baseUri, requestUri, 'GET', None,
            MapPropertiesDelegate(), self.applicationHandler.getConfiguration()
        )
        request.setEntityStream(InputStream.nullInputStream())
        self.applicationHandler.handle(request)
