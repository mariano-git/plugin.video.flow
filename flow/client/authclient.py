from piggy.base.util import Objects
from piggy.base.util.logging import Logger

from flow.api.auth import AuthApi
from flow.client import BaseClient
from flow.model.auth import LoginData, LoginModel
from plugin import PlugInUtils
from plugin.config import Settings, ApiData, Access, ApiServers


class AuthClient(BaseClient):
    __lg__ = Logger.getLogger(f'{__name__}.{__qualname__}')

    def login(self):
        loginData: LoginData = LoginData()
        access = Settings.of(Access)
        apiData = Settings.of(ApiData)

        casId = access.get(Access.CAS_ID)
        if Objects.isEmpty(casId):
            casId = PlugInUtils.CASID()
            access.set(Access.CAS_ID, casId)

        loginData.clientCasId = casId

        loginData.accountId = access.get(Access.USERNAME)
        loginData.password = access.get(Access.PASSWORD)

        loginData.deviceName = apiData.get(ApiData.DEVICE_NAME)
        loginData.deviceType = apiData.get(ApiData.DEVICE_TYPE)
        loginData.devicePlatform = apiData.get(ApiData.PLATFORM)

        loginData.version = apiData.get(ApiData.VERSION)
        loginData.type = apiData.get(ApiData.TYPE)
        loginData.deviceModel = apiData.get(ApiData.DEVICE_MODEL)
        loginData.company = apiData.get(ApiData.COMPANY)

        api: AuthApi = self.createResource(Settings.of(ApiServers).get(ApiServers.MAIN), AuthApi)

        response: LoginModel = api.login(loginData)
        return response

    def fetchToken(self):
        pass

    def checkDevice(self) -> bool:
        api: AuthApi = self.createResource(Settings.of(ApiServers).get(ApiServers.MAIN), AuthApi)
        return api.device()
