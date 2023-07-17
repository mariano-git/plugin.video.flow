from typing import List, Tuple

from flow import FlowConstants
from flow.model.content import FlowImage, FlowResource
from plugin import PlugInConstants
from plugin.config import Settings, ApiServers
from plugin.provider.epg.model.epg import EpgResource
from plugin.util import Converter


class ImageToUrlConverter(Converter[List[FlowImage], str]):

    def __init__(self, imgType: str, size: Tuple[int, int]):
        # Try to find the best image for the current purpose
        self.imgType = imgType
        self.size = size
        self.imageSource = Settings.of(ApiServers).get(ApiServers.IMAGES)

    def convert(self, sources: List[FlowImage]) -> str:
        logos: List[str] = list()

        if len(sources) == 1:
            # Try to use this image
            return sources[0].getImageUrl(
                self.imageSource
            )
        else:
            for source in sources:
                if source.usage == self.imgType:
                    return source.getImageUrl(
                        self.imageSource,
                        self.size[0],
                        self.size[1]
                    )
                else:
                    image: str = source.getImageUrl(
                        self.imageSource,
                        self.size[0],
                        self.size[1]
                    )
                logos.append(image)
        # FIXME: How to locate best image for this use?
        return logos[0]


class ResourceToUrlConverter(Converter[List[FlowResource], str]):
    # TODO: Remove useless since last api changes
    def convert(self, sources: List[FlowResource]) -> List[EpgResource]:
        resources: List[str] = list()
        DPR = FlowConstants.DASH_PATH_REPLACE
        for resource in sources:
            if resource.protocol in PlugInConstants.STREAMING_PROTOCOLS and \
                    resource.encryption in PlugInConstants.STREAMING_ENCRYPTIONS:
                resources.append(
                    resource.url.replace(DPR[0], DPR[1])
                )

        return resources[0]
