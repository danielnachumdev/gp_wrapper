from enum import Enum
from .....utils import Printable


class ContentCategory(Enum):
    """
    https://developers.google.com/photos/library/reference/rest/v1/mediaItems/search#contentcategory
    """
    NONE = "NONE"
    LANDSCAPES = "LANDSCAPES"
    RECEIPTS = "RECEIPTS"
    CITYSCAPES = "CITYSCAPES"
    LANDMARKS = "LANDMARKS"
    SELFIES = "SELFIES"
    PEOPLE = "PEOPLE"
    PETS = "PETS"
    WEDDINGS = "WEDDINGS"
    BIRTHDAYS = "BIRTHDAYS"
    DOCUMENTS = "DOCUMENTS"
    TRAVEL = "TRAVEL"
    ANIMALS = "ANIMALS"
    FOOD = "FOOD"
    SPORT = "SPORT"
    NIGHT = "NIGHT"
    PERFORMANCES = "PERFORMANCES"
    WHITEBOARDS = "WHITEBOARDS"
    SCREENSHOTS = "SCREENSHOTS"
    UTILITY = "UTILITY"
    ARTS = "ARTS"
    CRAFTS = "CRAFTS"
    FASHION = "FASHION"
    HOUSES = "HOUSES"
    GARDENS = "GARDENS"
    FLOWERS = "FLOWERS"
    HOLIDAYS = "HOLIDAYS"


class ContentFilter(Printable):
    """
    https://developers.google.com/photos/library/reference/rest/v1/mediaItems/search#contentfilter
    """

    def __init__(self, includedContentCategories: list[ContentCategory], excludedContentCategories: list[ContentCategory]) -> None:
        self.includedContentCategories = includedContentCategories
        self.excludedContentCategories = excludedContentCategories
