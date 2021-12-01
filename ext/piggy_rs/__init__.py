from typing import Any

from ext.piggy_rs.invoker import PiggyInvoker
from ext.ws.rs.client import Client


class WebResourceFactory:
    class ResourceDelegate:
        def __init__(self, resource: Any, client: Client, *args, **kargs):
            self.resource = resource
            self.client = client

        def examine(self, *args, **kwargs):
            pass

        def __call__(self, *args, **kwargs):
            pass

        def __getattr__(self, *args, **kwargs):
            func = args[0]

            def wrapper(*args, **kwargs):
                piggyInvoker: PiggyInvoker = PiggyInvoker(client=self.client)
                return piggyInvoker.execute(api=self.resource.__name__, call=func, kwargs=kwargs)

            return wrapper

    @staticmethod
    def newResource(invoker: Any, client: Client) -> Any:
        return WebResourceFactory.ResourceDelegate(invoker, client)
