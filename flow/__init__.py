from typing import Final, Tuple


class FlowConstants:
    class ImageUse:
        DESCRIPTION: Final[str] = 'S_DESC'
        CHANNEL_LOGO: Final[str] = 'CH_LOGO'
        BROWSE: Final[str] = 'BROWSE'
        DETAILS: Final[str] = 'DETAILS'

    class ImageSize:
        W16XH16: Final[Tuple[int, int]] = (16, 16)
        W299XH168: Final[Tuple[int, int]] = (299, 168)
        W60XH40: Final[Tuple[int, int]] = (60, 40)
        W350XH500: Final[Tuple[int, int]] = (350, 500)
        W655XH364: Final[Tuple[int, int]] = (655, 364)
        W1920XH1080: Final[Tuple[int, int]] = (1920, 1080)

    class StreamingProtocol:
        DASH: Final[str] = 'DASH'
        HLS: Final[str] = 'HLS'
        HLSV3: Final[str] = 'HLSV3'

    class ItemType:
        PARENTAL: Final[str] = 'parental'
        EPG: Final[str] = 'epg'
        STRIPE: Final[str] = 'stripe'
        PAGE: Final[str] = 'page'

    EXCLUDED_ITEM_TYPES = [ItemType.PARENTAL, ItemType.EPG]

    class SourceType:
        PROFILE: Final[str] = 'profile'
        SEARCH: Final[str] = 'search'
        APPLICATION: Final[str] = 'application'
        FILTERS: Final[str] = 'filters'
        RECORDINGS: Final[str] = 'recordings'
        FAVORITES: Final[str] = 'favorites'
        SETTINGS: Final[str] = 'settings'

    SOURCE_TYPES_EXCLUDED = (SourceType.PROFILE, SourceType.APPLICATION)

    class StripeType:
        SYSTEM: Final[str] = 'System'
        CUSTOM: Final[str] = 'Custom'

    class PageType:
        CONTENT: Final[str] = 'Content'

    class ContentType:
        RADIO_STATION: Final[str] = 'RADIO'
        TV_CHANNEL: Final[str] = 'TV_CHANNEL'
        TV_SCHEDULE: Final[str] = 'TV_SCHEDULE'
        VOD_SERIES: Final[str] = 'VOD_SERIES'
        ASSET: Final[str] = 'ASSET'
        DYNAMIC_ROOT_VOD: Final[str] = 'DYNAMIC_ROOT_VOD'
        VOD: Final[str] = 'VOD'
        PPV: Final[str] = 'PPV'
        # Stripes
        SETTINGS: Final[str] = 'Settings'
        ADVERTISEMENT: Final[str] = 'advertisement'
        APP: Final[str] = 'Application'
        LIVE_TV: Final[str] = 'LiveTV'
        CHANNELS: Final[str] = 'Channels'
        FAVORITES: Final[str] = 'Favorites'
        PROFILE: Final[str] = 'Profile'
        RECORDINGS: Final[str] = 'Recordings'
        CONTINUE_WATCHING: Final[str] = 'Continue Watching'
        RECENT_SEARCHES: Final[str] = 'Recent Searches'
        LAST_CHANGE_TO_WATCH: Final[str] = 'Last Chance To Watch'
        SEARCH: Final[str] = 'Search'
        MY_LIBRARY: Final[str] = 'My Library'
        MIXED: Final[str] = 'Mixed'

    CONTENT_TYPES_EXCLUDED = (ContentType.SETTINGS, ContentType.APP, ContentType.PROFILE,
                              ContentType.PPV, ContentType.FAVORITES, ContentType.LIVE_TV,
                              ContentType.SEARCH, ContentType.ADVERTISEMENT)

    DASH_PATH_REPLACE = ['/SA_Live_dash_enc/', '/SA_Live_dash_enc_2A/']

    ITEM_ADULT_ID: Final[int] = 300

    ITEMS_EXCLUDED = (ITEM_ADULT_ID,)

    FILTER_ADULT_ID: Final[int] = 1101
    STRIPE_ADULT_ID: Final[int] = 227

    STRIPE_DYNAMIC_STRIPE_COPY_ID: Final[int] = 960  # ?
    STRIPE_LIVE_TV_ID: Final[int] = 200
    STRIPE_ID_EXCLUDED = [STRIPE_ADULT_ID, 229, STRIPE_DYNAMIC_STRIPE_COPY_ID, STRIPE_LIVE_TV_ID]
