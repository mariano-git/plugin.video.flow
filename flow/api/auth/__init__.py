from typing import List

from ext.util import ModelHelper
from ext.ws.rs import Path, POST, Produces, Consumes, GET
from ext.ws.rs.core import MediaType


class LoginData(ModelHelper):
    accountId: str
    password: str
    deviceName: str
    deviceType: str
    devicePlatform: str
    clientCasId: str
    version: str
    type: str
    deviceModel: str
    company: str


class LoginResponse(ModelHelper):
    pass


class AccountId(ModelHelper):
    pass


class CacheTokenResponse(ModelHelper):
    pass


class UserDataResponse(ModelHelper):
    pass


class UserDataList:
    def __init__(self, data: List):
        self.users = []
        for user in data:
            self.users.append(UserDataResponse(**user))

    def getUsers(self):
        return self.users


@Path('auth/v2')
class AuthApi:

    @POST
    @Produces(MediaType.APPLICATION_JSON)
    @Consumes(MediaType.APPLICATION_JSON)
    @Path('provision/login')
    def login(self, loginData: LoginData) -> LoginResponse:
        pass

    def logout(self):
        pass

    @POST
    @Produces(MediaType.APPLICATION_JSON)
    @Consumes(MediaType.APPLICATION_JSON)
    @Path('provision/account')
    def account(self, accountId: AccountId) -> str:
        pass

    @GET
    @Path('cachetoken')
    @Consumes(MediaType.APPLICATION_JSON)
    def cacheToken(self) -> CacheTokenResponse:
        pass

    @GET
    @Path('device')
    @Consumes(MediaType.APPLICATION_JSON)  # text/plain?
    def device(self) -> bool:
        pass

    @GET
    @Path('userdata')
    def getUserData(self) -> UserDataList:
        pass
