from typing import NewType, List


class DisplayName:
    pass


class Icon:
    pass


class Channel:
    displayName: NewType('display-name', DisplayName)  # type: ignore
    icon: Icon


class Title:
    pass


class Desc:
    pass


class Category:
    pass


class Programme:
    title: Title
    desc: Desc
    category: Category
    icon: Icon


class XmlTv:
    channels: List[Channel]
    programs: List[Programme]


class XmlTvChannels:
    channels: List[Channel]
