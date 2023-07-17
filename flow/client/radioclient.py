from flow.api.radio import RadioApi
from flow.model.radio import RadioStations, RadioConfig
from piggy.restful.client.clientresourcefactory import ClientResourceFactory
from piggy.restful.ext.spi.json.jsonfeature import JsonFeature
from ws.rs.client.client import Client
from ws.rs.client.clientbuilder import ClientBuilder


class RadioClient:
    def __init__(self):
        self.client: Client = ClientBuilder.newClient()
        self.client.register(JsonFeature)
        self.radioApi = ClientResourceFactory.newResource(RadioApi, self.client)
        self.startIdx = 0
        self.busy = False

    def getStations(self) -> RadioStations:
        stations: RadioStations = self.radioApi.getStations()
        return stations

    def getConfig(self) -> RadioConfig:
        config: RadioConfig = self.radioApi.getRadioConfig()
        return config
