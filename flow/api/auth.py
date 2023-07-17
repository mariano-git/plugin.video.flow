from typing import List

from flow.client.support import JwtAuthentication
from flow.model.auth import LoginData, LoginModel, Account, CacheToken
from ws.rs.consumes import Consumes
from ws.rs.core.mediatype import MediaType
from ws.rs.httpmethod import POST, GET
from ws.rs.path import Path
from ws.rs.produces import Produces


@Path('auth/v2')
class AuthApi:

    @POST
    @Produces({MediaType.APPLICATION_JSON})
    @Consumes({MediaType.APPLICATION_JSON})
    @Path('provision/login')
    def login(self, loginData: LoginData) -> LoginModel:
        pass

    def logout(self):
        pass

    @POST
    @Produces({MediaType.APPLICATION_JSON})
    @Consumes({MediaType.APPLICATION_JSON})
    @Path('provision/account')
    def account(self, accountId: str) -> str:
        pass

    @GET
    @Path('cachetoken')
    @Consumes({MediaType.APPLICATION_JSON})
    def cacheToken(self) -> CacheToken:
        pass

    @GET
    @Path('device')
    @Consumes({MediaType.APPLICATION_JSON})  # text/plain?
    @JwtAuthentication
    def device(self) -> bool:
        pass

    @GET
    @Path('userdata')
    def getUserData(self) -> List[Account]:
        pass
