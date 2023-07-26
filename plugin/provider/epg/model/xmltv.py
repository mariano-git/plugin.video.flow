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


class Director:
    pass


class Writer:
    pass


class Actor:
    pass


class Value:
    pass


class Credits:
    director: Director
    writer: Writer
    actor: Actor


class StarRating:
    value: Value


class Date:
    pass


class EpisodeNum:
    pass


class SubTitle:
    pass


class Programme:
    title: Title
    desc: Desc
    category: Category
    icon: Icon
    subTitle: NewType('sub-title', SubTitle)  # type: ignore
    date: Date
    starRating: NewType('star-rating', StarRating)  # type: ignore
    episodeNum: NewType('episode-num', EpisodeNum)  # type: ignore
    credits: Credits


class XmlTv:
    channels: List[Channel]
    programs: List[Programme]


class XmlTvChannels:
    channels: List[Channel]
