from typing import Optional, List

from piggy.base.util import Objects
from piggy.base.util.concurrent.timeunit import TimeUnit

from flow.client.contentclient import ContentClient
from flow.model.content import FlowProgram
from plugin import PlugInUtils
from plugin.config import Settings, Programs, Access
from plugin.provider.epg.converter.flowprogram2xml import FlowProgram2XmlConverter
from plugin.provider.epg.stage import BaseRetriever
from plugin.stage import StageContext, StageException
from plugin.util import ProgressIndicator
from plugin.util.time import Time


class ProgramsRetriever(BaseRetriever):
    def __init__(self):
        self.xmlConverter = FlowProgram2XmlConverter()
        self.modes = None
        self.programs = set()
        self.mode = None
        self.lastSawProgram = 0

    class RunMode:
        def __init__(self, mode: bool, channels: List[int], time: Time, ratio: int, rating: int, wait: float,
                     segmentSize: int,
                     queriesCount: int, size: int, progress: ProgressIndicator, autoImport: bool):
            self.start, self.end = self.getTimeFrame(time, ratio)
            self.segments: List[List[int]] = self.createSegments(segmentSize, channels)
            self.queries = queriesCount
            self.size = size
            self.progress: ProgressIndicator = progress
            self.progress.update(0)
            self.isImport = autoImport
            self.fast = mode
            self.wait = wait
            self.rating = rating
            # FIXME
            self.progress.setTotal((ratio * len(channels)) * 2)  # guestimated

        def getTimeFrame(self, fromTime: Time, hoursRatio: int):
            # if hours ratio is greater than 48 then first 24 belong to yesterday.
            # programs don't seems to live more than that
            time = fromTime.UTC()
            if hoursRatio > 48:
                begin = time.substract(24, TimeUnit.HOURS)
                he = hoursRatio - 24
                end = time.add(he, TimeUnit.HOURS)
            else:
                begin = time.substract(hoursRatio, TimeUnit.HOURS)
                end = time.add(hoursRatio, TimeUnit.HOURS)
            return begin.toMillis(), end.toMillis()

        def createSegments(self, segmentSize: int, channels: List[int]) -> List[List[int]]:
            segments = list()
            for i in range(0, len(channels), segmentSize):
                segments.append(channels[i:i + segmentSize])
            return segments

    def setLast(self, startTime: int):
        self.lastSawProgram = startTime if startTime > self.lastSawProgram else self.lastSawProgram

    def store(self, logger, message):
        if not Objects.isEmpty(self.programs):
            logger.debug(message, len(self.programs))
            self.saveProgramsEpg(logger, self.programs)
            self.programs = set()

    def retrieve(self, context: StageContext, settings: Programs):
        logger = context.getLogger(self)
        if Objects.isEmpty(self.modes) and Objects.isEmpty(self.mode.segments):
            self.store(logger, 'Saving all collected programs: (%s) and end.')
            self.modes = None
            self.mode = None
            self.programs = set()
            settings.setLast(self.lastSawProgram)
            self.lastSawProgram = 0
            context.wait(self.MEDIUM_WAIT)
            return True

        if not Objects.isEmpty(self.modes) and Objects.isEmpty(self.mode.segments):
            if self.mode.fast:
                self.store(logger, 'Saving %s programs in fast mode')
                PlugInUtils.refreshEpg()
            self.mode = self.modes.pop(0)

        client: ContentClient = context.getComponent(ContentClient)
        i = 0
        r = range(0, self.mode.queries)
        context.wait(self.mode.wait / 1000)

        while i in r and not Objects.isEmpty(self.mode.segments):
            try:
                segment = self.mode.segments.pop(0)
                logger.info('Getting %s channels content', segment)
                programList: List[List[FlowProgram]] = client.getPrograms(channelIds=segment,
                                                                          size=self.mode.size,
                                                                          start=self.mode.start,
                                                                          end=self.mode.end,
                                                                          tvRating=self.mode.rating)
                for programs in programList:
                    for program in programs:
                        self.setLast(program.startTime)
                        self.programs.add(self.xmlConverter.convert(program))
                        self.mode.progress.refresh(1)
                i += 1
            except Exception as e:
                logger.warning('Exception fetching programs %s',e)

    def fast(self, context:StageContext, settings:Programs, channels):
        progress: ProgressIndicator
        if settings.isEnabled(Programs.EMERGENCY_SHOW_PROGRESS):
            progress = ProgressIndicator.of(0, 'Cargando...', 'Cargando Programas desde Flow')
        else:
            progress = ProgressIndicator.ofNull()
        progress.update(0)
        self.modes.append(
            ProgramsRetriever.RunMode(
                True,  # mode
                channels,  # channels
                Time.ofNow().atZero(TimeUnit.MINUTES),  # time
                settings.get(settings.EMERGENCY_TOTAL_HOURS),
                Settings.of(Access).get(Access.TV_RATING),
                settings.get(settings.EMERGENCY_WAIT_PER_RUN),  # wait
                settings.get(settings.EMERGENCY_CHANNELS_PER_QUERY),  # segmentSize
                settings.get(settings.EMERGENCY_QUERY_PER_RUN),  # queriesCount
                settings.get(settings.EMERGENCY_PROGRAMS_PER_QUERY),  # size
                progress,  # progress
                True,  # autoimport
            )

        )
        self.slow(context, settings, channels)

    def slow(self, context:StageContext, settings:Programs, channels):
        progress: ProgressIndicator
        if settings.isEnabled(Programs.SHOW_PROGRESS):
            progress = ProgressIndicator.of(0, 'Cargando...', 'Cargando Programas desde Flow')
        else:
            progress = ProgressIndicator.ofNull()
        progress.update(0)
        self.modes.append(
            ProgramsRetriever.RunMode(
                False,
                channels,
                Time.ofNow().atZero(),
                settings.get(settings.NORMAL_TOTAL_HOURS),
                Settings.of(Access).get(Access.TV_RATING),
                settings.get(settings.NORMAL_WAIT_PER_RUN),
                settings.get(settings.NORMAL_CHANNELS_PER_QUERY),
                settings.get(settings.NORMAL_QUERIES_PER_RUN),
                settings.get(settings.NORMAL_PROGRAMS_PER_QUERY),
                progress,
                True,
            )
        )
        self.mode = self.modes.pop(0)

    def execute(self, context: StageContext) -> Optional[bool]:
        programSettings = Settings.of(Programs)
        if programSettings.isTVScheduleCurrent():
            return True
        if self.modes is not None:
            return self.retrieve(context, programSettings)
        channels = self.getChannels()
        if channels is not None:
            tvchannels = list(map(lambda c: int(c.id), filter(lambda c: c.id.isnumeric(), channels.channels)))
        else:
            raise StageException('No Channels')
        self.modes = list()
        if programSettings.isTVScheduleExpired():
            return self.fast(context, programSettings, tvchannels)
        else:
            return self.slow(context, programSettings, tvchannels)
