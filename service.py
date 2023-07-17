from plugin import PlugInUtils
from plugin.service.executor import ServiceExecutor
from plugin.service.main import Service

PlugInUtils.initLogger()
if __name__ == "__main__":
    service = Service()
    service.configure()
    executor: ServiceExecutor = service.getExecutor()

    executor.execute()

    exit(0)
