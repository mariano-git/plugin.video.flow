from abc import abstractmethod
from typing import List, Any


class ClientRequestContext:
    def __init__(self,method, url, headers, query, body):
        self.method = method
        self.url = url
        self.headers = headers
        self.query = query
        self.body = body


class ClientResponseContext:
    def __init__(self, code,headers,body):
        self.code = code
        self.headers = headers
        self.body = body


class ClientRequestFilter:
    @abstractmethod
    def filter(self, requestContext: ClientRequestContext):
        pass


class ClientResponseFilter:
    @abstractmethod
    def filter(self, requestContext: ClientRequestContext, responseContext: ClientResponseContext):
        pass


class WebTarget:
    def __init__(self, uri: str):
        self.targetUri = uri


class Client:
    def __init__(self):
        self.webTarget: WebTarget = None
        self.filters: List[Any] = []

    def target(self, param) -> WebTarget:
        self.webTarget = WebTarget(param)
        return self.webTarget

    def register(self, provider):
        self.filters.append(provider)


class ClientBuilder:
    @staticmethod
    def newClient() -> Client:
        return Client()
