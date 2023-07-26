from typing import List, Optional
from urllib.parse import urlparse

from piggy.base.stringbuilder import StringBuilder
from piggy.restful.utils import SafeObject

from flow import FlowConstants


class FlowImage(SafeObject):

    def getImageUrl(self, url: str, w: Optional[int] = None, h: Optional[int] = None) -> str:
        sb = StringBuilder()

        parsed = urlparse(self.prefix)
        replace = urlparse(url)
        self.prefix = parsed._replace(scheme=replace.scheme, netloc=replace.netloc).geturl()
        if w is None and h is None:
            w = FlowConstants.ImageSize.W350XH500[0]
            h = FlowConstants.ImageSize.W350XH500[1]
        sb.append(
            self.prefix
        ).append('/').append(w).append('/').append(h).append('/0/0/').append(
            self.suffix
        ).append('.').append(self.format)
        return sb.toString()


class FlowResource(SafeObject):
    pass


class FlowProgram(SafeObject):
    images: List[FlowImage]
    resources: List[FlowResource]


class FlowChannel:
    images: List[FlowImage]
    resources: List[FlowResource]


class FlowVODContent(SafeObject):
    pass
