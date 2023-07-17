from typing import Dict


class DRMHeadersBuilder:
    def __init__(self):
        self.jwt = None
        self.token = None
        self.accept = None
        self.origin = None
        self.referer = None
        self.contentType = None

    @staticmethod
    def builder() -> 'DRMHeadersBuilder':
        return DRMHeadersBuilder()

    def withJwt(self, value: str) -> 'DRMHeadersBuilder':
        self.jwt = value
        return self

    def withToken(self, value: str) -> 'DRMHeadersBuilder':
        self.token = value
        return self

    def withAccept(self, value: str) -> 'DRMHeadersBuilder':
        self.accept = value
        return self

    def withOrigin(self, value: str) -> 'DRMHeadersBuilder':
        self.origin = value
        return self

    def withReferer(self, value: str) -> 'DRMHeadersBuilder':
        self.referer = value
        return self

    def withContentType(self, value: str) -> 'DRMHeadersBuilder':
        self.contentType = value
        return self

    def build(self) -> str:
        accept = 'accept=*/*' if self.accept is None else f'accept={self.accept}'
        template = {
            'origin': self.origin,
            'referer': self.referer,
            'authorization': f'Bearer {self.jwt}',
            'content-type': self.contentType,
            'drm-token': f'{self.token}',
        }
        headers = accept
        for k, v in template.items():
            # Weird shit happens if don't replace it. Eventually should be urlencoded
            headers += f'&{k}={v.replace("=", "%3D")}'
        return headers
