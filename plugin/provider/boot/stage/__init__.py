import xbmcgui

from piggy.base.util import Objects
from plugin.config import Settings, Access
from plugin.stage import Stage, StageContext, StageException


class CheckConfig(Stage):

    def execute(self, context: StageContext):
        access = Settings.of(Access)
        context.getLogger(self).debug('execute')
        userName = access.get(Access.USERNAME)
        passwd = access.get(Access.PASSWORD)

        if Objects.isEmpty(userName) or Objects.isEmpty(passwd):
            context.wait(Stage.LONG_WAIT)
            raise StageException('Invalid configuration.')
        return True


class DisplayConfigurationMessage(Stage):
    def execute(self, context: StageContext):
        context.getLogger(self).debug('execute')
        if context.getProperty('check.config.message.show') is None:
            d = xbmcgui.Dialog()
            msg = "Necesitas configurar el plugin para poder utilizarlo\n\n" \
                  "- Ve a la sección addons y alli configura\n" \
                  "- tu usuario y password de Flow"
            d.ok("FLOW - Configuracion incompleta...", msg)
            context.setProperty('check.config.message.show', True)
            # TODO
            # xbmcaddon.openSettings

            # Do not return means to stay on this road (I like a-ha)


class Resume(Stage):

    # TODO Should I give more logic to this stage?

    def execute(self, context: StageContext):
        logger = context.getLogger(self)
        tracker = context.getTracking()
        item = tracker.error.pop()
        if item:
            logger.debug('Recovered failed item: %s', item)
            context.disjoint(item['current'])
            return True
        raise StageException(f"Couldn't find a failed item on: {tracker.error}")
