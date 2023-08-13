from enum import Enum
from .....utils import Printable


class Feature(Enum):
    """
    https://developers.google.com/photos/library/reference/rest/v1/mediaItems/search#feature
    """
    NONE = "NONE"
    FAVORITES = "FAVORITES"


class FeatureFilter(Printable):
    """
    https://developers.google.com/photos/library/reference/rest/v1/mediaItems/search#featurefilter
    """

    def __init__(self, includedFeatures: list[Feature]) -> None:
        self.includedFeatures = includedFeatures
