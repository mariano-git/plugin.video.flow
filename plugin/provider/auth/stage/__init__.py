from piggy.base.util.date import Date
from ws.rs.forbiddenexception import ForbiddenException
from ws.rs.notauthorizedexception import NotAuthorizedException

from flow.client.authclient import AuthClient
from flow.model.auth import LoginModel
from plugin.config import Settings, JWT, PRM, Access
from plugin.stage import Stage, StageContext


class IsJWTValid(Stage):

    def execute(self, context: StageContext):

        if Settings.of(JWT).isCurrent():
            return True
        else:
            return False


class DoLogin(Stage):

    def execute(self, context: StageContext):
        client: AuthClient = context.getComponent(AuthClient)
        logger = context.getLogger(self)
        # TODO: Save or see how to manage extra Access information. At this time is irrelevant.

        response: LoginModel = client.login()
        jwt = Settings.of(JWT)
        jwt.set(JWT.VALUE, response.jwt)
        jwt.setLast(Date().getTime())

        userSettings = Settings.of(Access)
        userSettings.set(Access.VUID, response.multiRightVuid)
        userSettings.set(Access.DEVICE_ID, response.deviceId)
        userSettings.set(Access.EXTERNAL_ID, response.externalID)
        # TODO: add profiles to handle tv rating and other stuff
        logger.debug('Access configuration updated successfuly.')
        return True


class CallDevice(Stage):
    def execute(self, context: StageContext):
        client: AuthClient = context.getComponent(AuthClient)
        # TODO: device call always return True?
        response: bool = client.checkDevice()
        if response:
            # FIXME - TODO
            # update jwt duration so we could adapt and effectively know when it expires, otherwise use threshold
            # Usually JWT would expire on its own time, but I'm not sure if that value is ok so I prefer this method
            jwt = Settings.of(JWT)
            last = jwt.getLast()
            jwt.setDuration(Date().getTime() - last)
        return response


class DestroyTokens(Stage):
    def execute(self, context: StageContext):
        Settings.of(JWT).revoke()
        Settings.of(PRM).revoke()
        # TODO Implement Token
        #Settings.of(Token).revoke()

        Settings.of(Access).revoke(Access.REVOKE_IDS)
        return True


class DestroyUserData(Stage):
    def execute(self, context: StageContext):
        # depending on the exception wipe certain data and leave other.
        exception = context.getError()
        # TODO Check real Exceptions...
        if isinstance(exception, ForbiddenException) or isinstance(exception, NotAuthorizedException):
            Settings.of(Access).revoke(Access.REVOKE_ALL)

        Settings.of(JWT).revoke()
        Settings.of(PRM).revoke()
        #Settings.of(Token).revoke()

        # TODO Show message?
        context.wait(Stage.LONG_WAIT)
        return True


class EvaluateJwtExpiration(Stage):
    def execute(self, context: StageContext):
        error = context.getError()
        logger = context.getLogger(self)
        if isinstance(error, NotAuthorizedException):
            destroyTokens = DestroyTokens()
            destroyTokens.execute(context)
            logger.info("Successfully handled NotAuthorizedException")
            return True
        # TODO Check this
        logger.warning("Don't know how to handle: %s - Returning FALSE", error, )
        return False
