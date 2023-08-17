from enum import Enum
from .....utils import Printable, Dictable, get_python_version
if get_python_version() < (3, 9):
    from typing import List as t_list  # pylint: disable=ungrouped-imports,redefined-builtin
else:
    from builtins import list as t_list  # type:ignore


class Feature(Enum):
    """
    https://developers.google.com/photos/library/reference/rest/v1/mediaItems/search#feature
    """
    NONE = "NONE"
    FAVORITES = "FAVORITES"


class FeatureFilter(Printable, Dictable):
    """
    https://developers.google.com/photos/library/reference/rest/v1/mediaItems/search#featurefilter
    """

    def __init__(self, includedFeatures: t_list[Feature]) -> None:
        self.includedFeatures = includedFeatures

    def to_dict(self) -> dict:
        # TODO validate that this is correct
        return {
            "includedFeatures": [e.value for e in self.includedFeatures]
        }
