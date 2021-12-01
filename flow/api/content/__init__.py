from typing import List

from ext.util import ModelHelper
from ext.ws.rs import *
from ext.ws.rs.core import MediaType


class Channel(ModelHelper):
    pass


class Program(ModelHelper):
    pass


class ProgramList:
    # For some reason this is a wrapped list
    def __init__(self, data: List):
        self.programs = []
        for items in data:
            for program in items:
                self.programs.append(Program(**program))

    def getPrograms(self):
        return self.programs


class ChannelList:
    def __init__(self, data: List):
        self.channels = []
        for channel in data:
            self.channels.append(Channel(**channel))

    def getChannels(self):
        return self.channels


@Path('api/v1')
class ContentApi(object):

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    @Consumes(MediaType.APPLICATION_JSON)
    @Path('content/channels')
    def getChannels(self) -> ChannelList:
        return 'magic'

    @POST
    @Produces(MediaType.APPLICATION_JSON)
    @Consumes(MediaType.APPLICATION_JSON)
    @Path('content/channel')
    def getPrograms(self, channelIds: BeanParam(),
                    size: QueryParam(name='size'),
                    start: QueryParam(name='dateFrom'),
                    end: QueryParam(name='dateTo'),
                    tvRating: QueryParam(name='tvRating') = 6) -> ProgramList:
        return 'magic'
