from enum import Enum
from .....utils import Printable


class MediaType(Enum):
    ALL_MEDIA = "ALL_MEDIA"
    VIDEO = "VIDEO"
    PHOTO = "PHOTO"


class MediaTypeFilter(Printable):
    def __init__(self, mediaTypes: list[MediaType]) -> None:
        self.mediaTypes = mediaTypes
