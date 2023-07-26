import concurrent
import queue
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List

from piggy.base import Raisable
from piggy.base.util.concurrent.timeunit import TimeUnit
from piggy.base.util.logging import Logger

from flow.client.contentclient import ContentClient
from flow.model.content import FlowProgram
from plugin.config import Settings, Programs, Access
from plugin.provider.epg.converter.flowprogram2xml import FlowProgram2XmlConverter
from plugin.provider.epg.stage import BaseRetriever
from plugin.stage import StageContext, StageException, Stage
from plugin.util.time import Time


class TimeFrame:
    def __init__(self, start, end):
        self.startTime = start
        self.endTime = end


class Query:
    def __init__(self, start, end, channels):
        self.startTime = start
        self.endTime = end
        self.channels = channels


class Fetcher:
    __lg__ = Logger.getLogger(f'{__name__}.{__qualname__}')

    def __init__(self, retriever):
        self.client = ContentClient()
        self.retriever = retriever
        self.xmlConverter = FlowProgram2XmlConverter()
        self.lastSawProgram = -1

    def setLast(self, startTime: int):
        self.lastSawProgram = startTime if startTime > self.lastSawProgram else self.lastSawProgram

    def getLast(self):
        last = self.lastSawProgram
        self.lastSawProgram = -1
        return last

    def fetch(self):
        query = None
        try:
            query = self.retriever.queries.get(block=False)
        except queue.Empty as empty:
            query = None
        if query:
            try:
                programList: List[List[FlowProgram]] = self.client.getPrograms(channelIds=query.channels,
                                                                               size=self.retriever.size,
                                                                               start=query.startTime.toMillis(),
                                                                               end=query.endTime.toMillis(),
                                                                               tvRating=self.retriever.tvRating)
                for programs in programList:
                    for program in programs:
                        self.setLast(program.startTime)
                        self.retriever.programs.put(self.xmlConverter.convert(program))
            except Raisable as r:
                self.retriever.queries.put(query)
                self.__lg__.exception('Raisable %s', r)
            except BaseException as be:
                self.retriever.queries.put(query)
                self.__lg__.exception('BaseException %s', be)

        return self.getLast()


class ProgramsRetriever(BaseRetriever):

    def __init__(self):
        self.queries = None
        self.programs = None
        # self.queryExecutor = None
        self.fetchers = None
        self.size = None
        self.tvRating = None
        self.lastProgram = -1

    def reset(self):
        # self.queryExecutor.shutdown(False)
        self.queries = None
        self.programs = None
        # self.queryExecutor = None
        self.fetchers = None
        self.size = None
        self.tvRating = None
        self.lastProgram = -1

    def createQueries(self, context, settings, xmltv):
        # How much future time to retrieve in total
        # consider future starting tomorrow at 00:00 or today at 24:00
        futureHours = settings.get(settings.NORMAL_TOTAL_HOURS)
        # Today at 00:00
        start = Time.ofNow().atZero(TimeUnit.HOURS)
        # if starts today, total to retrieve is:
        totalHours = 24 + futureHours
        # But, past programming is valid for 24 hrs.
        # How many hours of past programming we'll lose if we retrieve only today starting at 00:00?
        delta = 24 - round(Time.ofNow().delta(start, TimeUnit.HOURS))
        if delta > 1:
            # We lose more than 1 hour. We need to start yesterday at 00:00 as web does...
            # I assume this will leverage some kind of cache in server, otherwise is silly to ask for entire day knowing
            # that we need just 1 or 2 hours...
            start = Time.ofYesterday().atZero(TimeUnit.HOURS)
            # Total now is:
            totalHours = 48 + futureHours

        current = start
        timeframes = list()

        while totalHours > 0:
            end = current.add(TimeUnit.DAYS.toMillis(1) - 1, TimeUnit.MILLISECONDS)
            tf = TimeFrame(current, end)
            timeframes.append(tf)
            current = end.add(1, TimeUnit.MILLISECONDS)
            totalHours -= 24

        tvchannels = list(map(lambda c: int(c.id), filter(lambda c: c.id.isnumeric(), xmltv.channels)))
        # How much channels per query
        segmentSize = settings.get(settings.NORMAL_CHANNELS_PER_QUERY)

        self.queries = queue.Queue()
        for i in range(0, len(tvchannels), segmentSize):
            for tf in timeframes:
                self.queries.put(Query(tf.startTime, tf.endTime, tvchannels[i:i + segmentSize]))

    def prepare(self, context, settings, xmltv):
        # Set the wait
        context.wait(settings.get(settings.NORMAL_WAIT_PER_RUN) / 1000)
        self.createQueries(context, settings, xmltv)
        # Set current size and tvRating
        self.tvRating = Settings.of(Access).get(Access.TV_RATING)
        self.size = settings.get(settings.NORMAL_PROGRAMS_PER_QUERY)

        self.programs = queue.Queue()

        # How many simultaneous queries
        max = settings.get(settings.NORMAL_QUERIES_PER_RUN)
        self.queryExecutor = ThreadPoolExecutor(max_workers=max)
        self.fetchers = set()
        for i in range(0, max):
            self.fetchers.add(Fetcher(self))

    def store(self, logger, message):
        self.programs.task_done()
        if not self.programs.empty():
            programs = set()
            while True:
                try:
                    programs.add(self.programs.get(False))
                except queue.Empty as e:
                    break

            logger.info(message, len(programs))
            self.saveProgramsEpg(logger, programs)

    def retrieve(self, context, settings: Programs):
        logger = context.getLogger(self)
        if not self.queries.empty():

            for fetcher in self.fetchers:
                last = fetcher.fetch()
                self.lastProgram = last if last > self.lastProgram else self.lastProgram
            return
        self.store(logger, 'Saving all collected programs: (%s) and end.')
        settings.setLast(self.lastProgram)
        settings.updateLastRun()

        context.wait(self.MEDIUM_WAIT)
        self.reset()
        return True

    def execute(self, context: StageContext) -> Optional[bool]:
        programSettings = Settings.of(Programs)
        if programSettings.isTVScheduleCurrent():
            context.wait(Stage.LONG_WAIT)
            return True

        if not programSettings.isRunAllowed():
            context.getLogger(self).warning(
                'I cowardly refuse to run because it hasn\'t been long enough since I last ran'
            )
            return True

        if self.queries is not None:
            return self.retrieve(context, programSettings)

        xmltv = self.getXmlTv()

        if xmltv is not None and hasattr(xmltv, 'channels'):
            self.prepare(context, programSettings, xmltv)

        else:
            raise StageException('No Channels')
