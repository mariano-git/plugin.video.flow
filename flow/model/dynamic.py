from typing import List

from piggy.restful.utils import SafeObject


class Empty(SafeObject):
    def isEmpty(self) -> bool:
        return len(self.__dict__) == 0


class Nameable(Empty):
    def getName(self) -> str:
        titles = dict(map(lambda t: (t.language, t.title), self.titles if self.titles else self.name))
        return titles['es'] if 'es' in titles else titles['en']


class Title(Empty):
    pass


class PosterImageStyleConfiguration:
    pass


class StripeItem(Empty):
    titles: List[Title]
    posterImageStyleConfigurations: List[PosterImageStyleConfiguration]


class SourceInfo(Empty):
    stripeItems: List[StripeItem]

    def isEmpty(self) -> bool:
        return len(self.__dict__) == 0


class ImageTags(Empty):
    pass


class Configuration(Empty):
    pass


class Style(Empty):
    imageTags: ImageTags
    configuration: List[Configuration]


class Stripe(Nameable):
    titles: List[Title]
    sourceInfo: SourceInfo
    style: Style


class PageStripe(Empty):
    stripe: Stripe


class Page(Nameable):
    stripes: List[PageStripe]


class PageItem(Empty):
    page: Page


class Item(Nameable):
    stripe: Stripe
    page: Page
    name: List[Title]


class NavItem(Empty):
    item: Item


class NavPanel(Empty):
    navItems: List[NavItem]
    pages: List[PageItem]


class Content(Empty):
    navPanel: NavPanel


class DynamicAllModel:
    content: Content


class DynamicBulkModel:
    contents: List[Content]
