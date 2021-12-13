from ext.ws.rs.core import Response
from ext.ws.rs.ext import RuntimeDelegate


class RsAnnotation:
    def __init__(self, *args, **kwargs):
        self.arg = None if len(args) == 0 else args if len(args) > 1 else args[0]
        self.kwargs = None if len(kwargs) == 0 else kwargs
        RuntimeDelegate().register(self, self.arg, None)

    def __call__(self, callable, **kwargs):
        self.call_kwargs = None if len(kwargs) == 0 else kwargs

        RuntimeDelegate().register(self, callable, self.call_kwargs)

        return callable


class Produces(RsAnnotation):
    """
    Defines the media type(s) that the methods of a resource class or MessageBodyWriter can produce.
    If not specified then a container will assume that any type can be produced.
    Method level annotations override a class level annotation.
    A container is responsible for ensuring that the method invoked is capable of producing one of the media types requested in the HTTP request.
    If no such method is available the container must respond with a HTTP "406 Not Acceptable" as specified by RFC 2616.
    A method for which there is a single-valued @Produces is not required to set the media type of representations that it produces:
    the container will use the value of the @Produces when sending a response.
    """
    pass


class Consumes(RsAnnotation):
    """
    Defines the media types that the methods of a resource class or MessageBodyReader can accept.
    If not specified, a container will assume that any media type is acceptable.
    Method level annotations override a class level annotation.
    A container is responsible for ensuring that the method invoked is capable of consuming the media type of the HTTP
    request entity body.
    If no such method is available the container must respond with a HTTP "415 Unsupported Media Type" as specified by RFC 2616.
    String[]	value
    A list of media types.
    """
    pass


class HeaderParam(RsAnnotation):
    pass


class BeanParam(RsAnnotation):
    pass


class Path(RsAnnotation):
    pass


class QueryParam(RsAnnotation):
    pass


class GET(RsAnnotation):
    pass


class POST(RsAnnotation):
    pass


class WebApplicationException(RuntimeError):

    def __init__(self, message: str, cause: Exception = None, response: Response = None):
        self.cause = cause
        self.response: Response = response
        super().__init__(message)


class ClientErrorException(WebApplicationException):
    def __init__(self, message: str, cause: Exception = None, response: Response = None):
        super().__init__(message, cause, response)


class NotAuthorizedException(ClientErrorException):
    def __init__(self, message: str, cause: Exception = None, response: Response = None):
        super().__init__(message, cause, response)


class NotFoundException(ClientErrorException):
    def __init__(self, message: str, cause: Exception = None, response: Response = None):
        super().__init__(message, cause, response)
