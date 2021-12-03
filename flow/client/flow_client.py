import urllib
from typing import List
from urllib.parse import urlparse
from xml.etree import ElementTree

from ext.piggy_rs import WebResourceFactory
from ext.util import ModelHelper
from ext.ws.rs import NotAuthorizedException
from ext.ws.rs.client import ClientRequestFilter, \
    ClientResponseFilter, \
    ClientRequestContext, \
    ClientResponseContext, \
    Client, ClientBuilder, WebTarget
from flow.api.auth import LoginResponse, LoginData, AuthApi
from flow.api.content import ContentApi, ChannelList, ProgramList
from flow.api.prm import PrmApi, RegisterResponse, RegisterRequest
from flow.config import *

timeUtils: TimeUtils = TimeUtils()


def timeStamp(date, hour):
    _fmt = f"{date.year}-{date.month}-{date.day} {hour}"
    return timeUtils.toMillis(_fmt)


def yesterdayMillis():
    t = timeUtils.yesterday()
    return (
        timeStamp(t, "00:00:00.000"),
        timeStamp(t, "23:59:59.999"),
    )


def todayMillis():
    t = timeUtils.today()
    return (
        timeStamp(t, "00:00:00.000"),
        timeStamp(t, "23:59:59.999"),
    )


def tomorrowMillis():
    t = timeUtils.tomorrow()
    return [
        timeStamp(t, "00:00:00.000"),
        timeStamp(t, "23:59:59.999"),
    ]


def buildResources(resources):
    sources: List = list()
    for rsrc in resources:
        resource = ModelHelper(**rsrc)
        if resource.protocol in ['DASH', 'HLS', 'HLSV3']:
            sources.append(ChannelSource(**{
                'protocol': resource.protocol,
                'encryption': resource.encryption,
                'url': resource.url
            }))
    return sources


class ChannelSource(ModelHelper):
    pass


class Program:
    def __init__(self, flowProgram):
        self._id = flowProgram.id
        self.title = flowProgram.title
        self.start = flowProgram.startTime
        self.end = flowProgram.endTime
        self.description = flowProgram.description
        self.category = flowProgram.genre
        self.expire = flowProgram.ndvrExpire
        self.channelId = flowProgram.channelId
        self.programId = flowProgram.programId
        self.logo = self.__buildImages(flowProgram.images)
        self.sources = buildResources(flowProgram.resources)

    def __buildImages(self, images):

        for img in images:
            image = ModelHelper(**img)
            # if image.usage == 'BROWSE' and self.programId:
            #     return 'https://static.flow.com.ar/images/{prgId}/{usage}/{height}/{width}/0/0/{suffix}.{format}' \
            #         .format(prgId=self.programId, usage=image.usage, height=350, width=500, suffix=image.suffix,
            #                 format=image.format)
            # elif image.usage == 'BROWSE' and not self.programId:
            if image.usage == 'BROWSE':
                # 'http://geo.mnedge.cvattv.com.ar:9001/images/3646x20211127x0300/BROWSE
                path = urlparse(image.prefix).path
                return 'https://static.flow.com.ar/{path}/{height}/{width}/0/0/{suffix}.{format}' \
                    .format(path=path, usage=image.usage, height=350, width=500, suffix=image.suffix,
                            format=image.format)

    def toM3U(self):
        pass

    def toXML(self):
        pass

    def toXMLElement(self, parent):

        catchUpUri = f"plugin://plugin.video.flow/play?program={self._id}&type=TV_SCHEDULE"

        xmlProg = ElementTree.SubElement(parent, "programme",
                                         start=timeUtils.formatMills(self.start),
                                         stop=timeUtils.formatMills(self.end),
                                         channel=f"channel-{self.channelId}"
                                         )
        xmlProg.set('catchup-id', catchUpUri)
        ElementTree.SubElement(xmlProg, "title", lang="sp").text = self.title
        ElementTree.SubElement(xmlProg, "desc", lang="sp").text = self.description
        ElementTree.SubElement(xmlProg, "category", lang="sp").text = self.category
        ElementTree.SubElement(xmlProg, "icon", src=self.logo)
        # return xmlProg


class Channel:
    def __init__(self, flowChannel):
        self._id = flowChannel.id
        self.name = flowChannel.title
        self.number = flowChannel.number
        self.logo = self.__buildLogo(flowChannel.images)
        self.sources = buildResources(flowChannel.resources)
        self.contentType = flowChannel.contentType
        self.catchUp = None

        self.programs: List[Program] = list()

    def __buildLogo(self, images):

        for img in images:
            image = ModelHelper(**img)
            if image.usage != 'CH_LOGO':
                continue
            return 'https://static.flow.com.ar/images/{channel_id}/{usage}/{height}/{width}/0/0/{suffix}.{format}' \
                .format(channel_id=self._id, usage=image.usage, height=350, width=500, suffix=image.suffix,
                        format=image.format)

    @property
    def id(self):
        return self._id

    def addProgram(self, program: Program):
        self.programs.append(program)

    def toM3U(self):
        urlDash = ""
        for source in self.sources:
            if source.protocol == 'DASH':
                urlDash = urllib.parse.quote(source.url, safe="")

        catchUpSrc = 'catchup="vod"'

        entry = '#EXTINF:-1 ' \
                'tvg-chno="{chNum}" ' \
                'tvg-id="channel-{chId}" ' \
                'tvg-name="{chName}" ' \
                'tvg-logo="{chLogo}" ' \
                'group-title="Flow" ' \
                'radio="false" ' \
                '{catchUpSrc},{chName}\n' \
                'plugin://plugin.video.flow/play?channel={chId}&type={contentType}&source={source} \n'

        return entry.format(chId=self.id, chNum=self.number, chName=self.name, chLogo=self.logo,
                            contentType=self.contentType, source=urlDash, catchUpSrc=catchUpSrc)

    def toXML(self):
        xmlEntry = \
            '<channel id="channel-{chId}"> \
                <display-name lang="en">{chName}</display-name> \
            </channel>' \
                .format(chId=self.id, chName=self.name)
        return xmlEntry

    def toXMLElement(self, parent):
        xmlElem = ElementTree.SubElement(parent, "channel", id=f"channel-{self.id}")
        ElementTree.SubElement(xmlElem, "display-name", lang="en").text = self.name
        for program in self.programs:
            program.toXMLElement(parent)


class TvGuide:
    def __init__(self):
        self.channels: List[Channel] = list()
        self.times = [yesterdayMillis(), todayMillis(), tomorrowMillis()]
        self.__currentPeriod = 0

    def addChannel(self, channel: Channel):
        self.channels.append(channel)

    def getChannels(self):
        return self.channels

    def hasNextTimePeriod(self):
        return self.__currentPeriod + 1 < len(self.times)

    def currentTimePeriod(self):
        return self.times[self.__currentPeriod]

    def nextTimePeriod(self):
        self.__currentPeriod += 1

    def build(self):
        xml_tv = ElementTree.Element("tv")
        m3u = "#EXTM3U tvg-shift=0\n"
        for channel in self.channels:
            channel.toXMLElement(xml_tv)
            m3u += channel.toM3U()

        xmlFile = f"{getConfigPath()}tvguide.xml"
        m3uFile = f"{getConfigPath()}tvguide.m3u"

        xml_str: str = ElementTree.tostring(xml_tv, encoding="unicode", method="xml")

        text_file = open(xmlFile, "w", encoding="utf-8")
        text_file.write("<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n")

        text_file.write(xml_str)
        text_file.close()

        text_file = open(m3uFile, "w", encoding="utf-8")
        text_file.write(m3u)
        text_file.close()


class AuthorizationFeature(ClientRequestFilter, ClientResponseFilter):

    def __init__(self):
        self.jwt = getJwt()
        self.prm = getPrm()

    def filterRequest(self, requestContext: ClientRequestContext):
        if LOGIN_URL not in requestContext.url and self.prm is not None and CONTENT_SOURCE_URL in requestContext.url:
            requestContext.headers['Authorization'] = f"Bearer {self.prm}"
        elif LOGIN_URL not in requestContext.url and self.jwt is not None:
            requestContext.headers['Authorization'] = f"Bearer {self.jwt}"

    def filterRequestResponse(self, requestContext: ClientRequestContext, responseContext: ClientResponseContext):
        code = responseContext.code
        if code == 401 or code == 403:
            self.jwt = None
            invalidateJwt()
        else:
            bodyResponse = responseContext.body
            if isinstance(bodyResponse, LoginResponse):
                self.jwt = bodyResponse.jwt
                setJwt(self.jwt)
                setMultiRightVuid(bodyResponse.multiRightVuid)
            elif isinstance(bodyResponse, RegisterResponse):
                self.prm = bodyResponse.tokenForPRM
                setPrm(self.prm)

    def filter(self, requestContext: ClientRequestContext, responseContext: ClientResponseContext = None):
        if responseContext is not None:
            self.filterRequestResponse(requestContext=requestContext, responseContext=responseContext)
        else:
            self.filterRequest(requestContext=requestContext)


authFeature = AuthorizationFeature()


class ApiDriver:
    def __init__(self):
        self.client: Client = ClientBuilder.newClient()
        self.client.register(authFeature)
        self.target: WebTarget = self.client.target(getBaseUrl())
        self.authApi = WebResourceFactory.newResource(AuthApi, self.client)
        self.contentApi = WebResourceFactory.newResource(ContentApi, self.client)
        self.prmApi = WebResourceFactory.newResource(PrmApi, self.client)
        self.startIdx = 0
        self.tvGuide: TvGuide = None
        self.busy = False

    def isReady(self):
        for key in [SETTING_USER, SETTING_PASSWORD]:
            value = getSetting(key=key)
            if isBlank(value):
                return False
        return True

    def isJwtValid(self):

        if getJwt() is not None:
            return True

        try:
            check = self.authApi.device()
            Logger.log(f"isJwtValid: {check}")
            touchJwt()
            return True
        except NotAuthorizedException as nae:
            Logger.log_error(f"NotAuthorizedException: {nae}")
            return False

    def isPrmValid(self):
        if getPrm() is not None:
            return True
        return False

    def registerForPrm(self):
        prmRequest: RegisterRequest = RegisterRequest(
            deviceBrand="",
            deviceModel="",
            deviceType=API_DEVICE_TYPE,
            playerType=API_PLAYER_TYPE,
            networkType=API_NETWORK_TYPE
        )
        try:
            response: RegisterResponse = self.prmApi.register(registerPayload=prmRequest)
            return True
        except NotAuthorizedException as nae:
            Logger.log_error(f"NotAuthorizedException: {nae}")
        return False

    def doLogin(self):
        loginData: LoginData = LoginData(
            accountId=getUser(),
            password=getPassword(),
            deviceName=API_DEVICE_NAME,
            deviceType=API_DEVICE_TYPE,
            devicePlatform=API_DEVICE_PLATFORM,
            clientCasId=getClientCasId(),
            version=API_VERSION,
            type=API_TYPE,
            deviceModel=API_DEVICE_MODEL,
            company=API_COMPANY)
        try:
            response: LoginResponse = self.authApi.login(loginData=loginData)
            return True
        except NotAuthorizedException as nae:
            Logger.log_error(f"NotAuthorizedException: {nae}")
        return False

    def isEpgTime(self):
        lastEpg = getLastEpg()
        lastEpgDelta: int = timeUtils.currentMillis() - lastEpg
        threshold = getEpgThreshold()
        return lastEpgDelta > threshold

    def getChannels(self):
        self.tvGuide = TvGuide()
        channelList: ChannelList = self.contentApi.getChannels()
        for flowChannels in channelList.getChannels():
            self.tvGuide.addChannel(Channel(flowChannels))
        return True

    def getPrograms(self, tvRating: int = 6):
        # channels = [1, 2, 3, 4]
        # tvRating = 6

        if self.busy:
            return True

        self.busy = True

        size = 1440
        timePeriod = self.tvGuide.currentTimePeriod()

        channelIds: List[int] = list()

        fChannels = self.tvGuide.getChannels()
        quantity: int = 20
        length: int = len(fChannels)
        iterationEnd = self.startIdx + quantity

        finish = min(length, iterationEnd)

        chs = {}

        while self.startIdx < finish:
            ch = fChannels[self.startIdx]
            channelIds.append(int(ch.id))
            chs[ch.id] = ch
            self.startIdx += 1

        fPrograms: ProgramList = self.contentApi.getPrograms(channelIds=channelIds,
                                                             size=size,
                                                             start=timePeriod[0],
                                                             end=timePeriod[1],
                                                             tvRating=tvRating)

        for fProgram in fPrograms.getPrograms():
            chs[fProgram.channelId].addProgram(Program(fProgram))

        self.busy = False

        if self.startIdx < length:
            return True
        else:
            if self.tvGuide.hasNextTimePeriod():
                self.tvGuide.nextTimePeriod()
                self.startIdx = 0
                return True

        return False

    def buildFullEpg(self):
        self.tvGuide.build()
        touchEpg()
        self.startIdx = 0
        addon = xbmcaddon.Addon('pvr.iptvsimple')
        addon.setSetting('reload', 'reload')
        return True

    def contentSource(self, sourceId: str, sourceType: str):
        return self.prmApi.contentSource(sourceId=sourceId, sourceType=sourceType)
