import os
import sys

from plugin import PlugInUtils
from plugin.application import PlugInApplication
from plugin.spi.plugincontainer import PlugInContainer

PlugInUtils.initLogger()

if __name__ == "__main__":
    args = list(sys.argv)
    env = os.environ.get('ENVIRONMENT')
    if env == 'development':
        args.pop(0)

    if len(args) > 0:

        # check if this is a direct invocation and redirect to main.
        url = args[0]
        if url == 'plugin://plugin.video.flow/':
            args[0] = 'plugin://plugin.video.flow/main/index'

        container = PlugInContainer.create(PlugInApplication).start()
        container.service(args)
    else:
        print('Nothing to do...')
