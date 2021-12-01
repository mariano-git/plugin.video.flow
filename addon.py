import sys
from urllib.parse import urlparse, parse_qs

import xbmcaddon
import xbmcgui
import xbmcplugin

from ext.util.logger import Logger
from flow.api.prm import ContentSourceResponse
from flow.client.flow_client import ApiDriver
from flow.config import getMultiRightVuid, clearEpg


class Command:
    def __init__(self, args):
        cmdUri = urlparse(f"{args[0]}{args[2]}&handle={args[1]}&{args[3].replace(':', '=')}")
        self.verb = cmdUri.path.lstrip('/')
        self.arguments = self.simplify(parse_qs(cmdUri.query))

    def simplify(self, params):
        values = {}
        for key, value in params.items():
            values[key] = value if len(value) > 1 else value[0]
        return values


def getMPD(arguments: dict):
    sourceType = arguments['type']
    if 'TV_SCHEDULE' in sourceType:

        apiDriver: ApiDriver = ApiDriver()
        if not apiDriver.isPrmValid():
            apiDriver.registerForPrm()

        response: ContentSourceResponse = apiDriver.contentSource(arguments['program'], sourceType)
        return response.contentUrl.replace('http', 'https').replace('SA_Live_dash_enc', 'SA_Live_dash_enc_2A')
    else:
        return arguments['source']


# https://github.com/xbmc/inputstream.adaptive/wiki/Integration
def play(arguments):
    mpd = getMPD(arguments)
    handle: int = int(arguments['handle'])
    headers = 'Content-Type=&User-Agent=Mozilla/5.0 (X11; Linux x86_64) ' \
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36' \
              '&sec-ch-ua-platform="Linux"' \
              '&Origin=https://web.flow.com.ar' \
              '&Sec-Fetch-Site=cross-site' \
              '&Sec-Fetch-Mode=cors' \
              '&Sec-Fetch-Dest=empty' \
              '&Referer=https://web.flow.com.ar/'
    mode = '{SSM}'
    multiRight = getMultiRightVuid()

    LICENSE = f"https://wv-client.cvattv.com.ar/?deviceId={multiRight}|{headers}|R{mode}|"

    player = xbmcgui.ListItem(path=mpd)
    player.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
    player.setProperty('inputstream.adaptive.license_key', LICENSE)
    player.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    player.setProperty('inputstream', 'inputstream.adaptive')
    player.setMimeType('application/dash+xml')
    player.setContentLookup(False)

    xbmcplugin.setResolvedUrl(handle, True, listitem=player)


def doConfigureIpTv():
    iptvSettings = xbmcaddon.Addon(id='pvr.iptvsimple')
    iptvSettings.setSettingInt("m3uPathType", 0)
    iptvSettings.setSetting("m3uPath", "special://userdata/addon_data/plugin.video.flow/tvguide.m3u")
    iptvSettings.setSettingInt("epgPathType", 0)
    iptvSettings.setSetting("epgPath", "special://userdata/addon_data/plugin.video.flow/tvguide.xml")
    iptvSettings.setSettingBool("epgCache", False)
    iptvSettings.setSettingInt("logoFromEpg", 2)
    iptvSettings.setSettingBool("timeshiftEnabled", True)
    iptvSettings.setSettingBool("catchupEnabled", True)
    iptvSettings.setSettingBool("catchupPlayEpgAsLive", True)


Logger.log('Initializing')
if __name__ == "__main__":

    Logger.log(f"got URL: {sys.argv}")
    command: Command = Command(sys.argv)
    Logger.log(f"got command: {command} - {command.verb} - {command.arguments}")
    if command.verb == 'play':
        play(command.arguments)
    elif command.verb == 'rebuildEpg':
        clearEpg()
    elif command.verb == 'configureIPTV':
        doConfigureIpTv()
    else:
        exit(0)
