import enum
from typing import Optional


class RequestType(enum.Enum):
    GET = "get"
    POST = "post"
    PATCH = "patch"


class PositionType(enum.Enum):
    """enum to be used with GooglePhotosAlbum.add_enrichment to specify
    the relative location of the enrichment in the album
    """
    POSITION_TYPE_UNSPECIFIED = "POSITION_TYPE_UNSPECIFIED"
    FIRST_IN_ALBUM = "FIRST_IN_ALBUM"
    LAST_IN_ALBUM = "LAST_IN_ALBUM"
    AFTER_MEDIA_ITEM = "AFTER_MEDIA_ITEM"
    AFTER_ENRICHMENT_ITEM = "AFTER_ENRICHMENT_ITEM"


class EnrichmentType(enum.Enum):
    """enum to be used with GooglePhotosAlbum.add_enrichment to specify the type of enrichment
    """
    TEXT_ENRICHMENT = "textEnrichment"
    LOCATION_ENRICHMENT = "locationEnrichment"
    MAP_ENRICHMENT = "mapEnrichment"


class MaskTypes(enum.Enum):
    """
    available mask values to update for a media item
    see https://developers.google.com/photos/library/reference/rest/v1/mediaItems/patch#query-parameters
    """
    DESCRIPTION = "description"


class RelativeItemType(enum.Enum):
    relativeMediaItemId = "relativeMediaItemId",
    relativeEnrichmentItemId = "relativeEnrichmentItemId"


class SimpleMediaItem:
    def __init__(self, uploadToken: str, fileName: str) -> None:
        self.uploadToken = uploadToken
        self.fileName = fileName


class NewMediaItem:
    def __init__(self, description: str, simpleMediaItem: SimpleMediaItem) -> None:
        self.description = description
        self.simpleMediaItem = simpleMediaItem


class AlbumPosition:
    def __init__(self, position: PositionType, /, relativeMediaItemId: Optional[str] = None, relativeEnrichmentItemId: Optional[str] = None) -> None:
        self.position = position
        if (not relativeMediaItemId and not relativeEnrichmentItemId) \
                or (relativeEnrichmentItemId and relativeEnrichmentItemId):
            raise ValueError(
                "Must supply exactly one between 'relativeMediaItemId' and 'relativeEnrichmentItemId'")
        if relativeMediaItemId:
            self.relativeMediaItemId = relativeMediaItemId
        else:
            self.relativeEnrichmentItemId = relativeEnrichmentItemId

    def to_dict(self) -> dict:
        dct = self.__dict__.copy()
        dct["position"] = self.position.value
        return dct


Milliseconds = float
Seconds = float
MediaItemID = str
Url = str
AlbumId = str
Path = str
NextPageToken = str
relativeMediaItemId = str
relativeEnrichmentItemId = str
Value = str
SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary',
    "https://www.googleapis.com/auth/photoslibrary.appendonly",
    "https://www.googleapis.com/auth/photoslibrary.sharing",
    "https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata"
]
EMPTY_PROMPT_MESSAGE = ""
DEFAULT_NUM_WORKERS: int = 2
ALBUMS_ENDPOINT = "https://photoslibrary.googleapis.com/v1/albums"
UPLOAD_MEDIA_ITEM_ENDPOINT = "https://photoslibrary.googleapis.com/v1/uploads"
MEDIA_ITEMS_CREATE_ENDPOINT = "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"
