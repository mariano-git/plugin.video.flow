from typing import Set, Type

from plugin.application.main import MainEndpoint
from plugin.application.play import PlayEndpoint
from ws.rs.applicationpath import ApplicationPath
from ws.rs.core.application import Application

from plugin.application.setup import SetupEndpoint


@ApplicationPath("/")
class PlugInApplication(Application):

    def getClasses(self) -> Set[Type]:
        return {
            PlayEndpoint,
            SetupEndpoint,
            MainEndpoint
        }
