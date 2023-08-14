import json
from enum import Enum
from datetime import datetime
from typing import Optional
from abc import ABC, abstractmethod
import gp_wrapper  # pylint: disable=unused-import

Milliseconds = float
Seconds = float
MediaItemID = str
UploadToken = str
Url = str
AlbumId = str
Path = str
NextPageToken = str
Value = str


class RequestType(Enum):
    GET = "get"
    POST = "post"
    PATCH = "patch"


class PositionType(Enum):
    """enum to be used with GooglePhotosAlbum.add_enrichment to specify
    the relative location of the enrichment in the album
    """
    POSITION_TYPE_UNSPECIFIED = "POSITION_TYPE_UNSPECIFIED"
    FIRST_IN_ALBUM = "FIRST_IN_ALBUM"
    LAST_IN_ALBUM = "LAST_IN_ALBUM"
    AFTER_MEDIA_ITEM = "AFTER_MEDIA_ITEM"
    AFTER_ENRICHMENT_ITEM = "AFTER_ENRICHMENT_ITEM"


class EnrichmentType(Enum):
    """enum to be used with GooglePhotosAlbum.add_enrichment to specify the type of enrichment
    """
    TEXT_ENRICHMENT = "textEnrichment"
    LOCATION_ENRICHMENT = "locationEnrichment"
    MAP_ENRICHMENT = "mapEnrichment"


class MediaItemMaskTypes(Enum):
    """
    available mask values to update for a media item
    see https://developers.google.com/photos/library/reference/rest/v1/mediaItems/patch#query-parameters
    """
    DESCRIPTION = "description"


class AlbumMaskType(Enum):
    TITLE = "title"
    COVER_PHOTOS_MEDIA_ITEM_ID = "coverPhotoMediaItemId"


class RelativeItemType(Enum):
    relativeMediaItemId = "relativeMediaItemId",
    relativeEnrichmentItemId = "relativeEnrichmentItemId"


class Printable:
    def __str__(self) -> str:
        return f"{self.__class__.__name__} {json.dumps(self.__dict__,indent=4,default=gp_wrapper.utils.json_default)}"


class Dictable(ABC):
    @abstractmethod
    def to_dict(self) -> dict: ...


class SimpleMediaItem(Dictable, Printable):
    # see https://developers.google.com/photos/library/reference/rest/v1/mediaItems/batchCreate#SimpleMediaItem
    def __init__(self, uploadToken: str, fileName: str) -> None:
        self.uploadToken = uploadToken
        self.fileName = fileName

    def to_dict(self) -> dict:
        return self.__dict__


class NewMediaItem(Dictable, Printable):
    @staticmethod
    def from_dict(token: UploadToken, description: str = "", filename: str = "") -> "NewMediaItem":
        return NewMediaItem(
            description,
            SimpleMediaItem(
                token,
                filename
            )
        )

    def __init__(self, description: str, simpleMediaItem: SimpleMediaItem) -> None:
        self.description = description
        self.simpleMediaItem = simpleMediaItem

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "simpleMediaItem": self.simpleMediaItem.to_dict()
        }


class AlbumPosition(Dictable, Printable):
    def __init__(self, position: PositionType = PositionType.FIRST_IN_ALBUM, /,
                 relativeMediaItemId: Optional[str] = None,
                 relativeEnrichmentItemId: Optional[str] = None) -> None:
        self.position = position
        if position in {PositionType.AFTER_MEDIA_ITEM, PositionType.AFTER_ENRICHMENT_ITEM}:
            if (not relativeMediaItemId and not relativeEnrichmentItemId) \
                    or (relativeEnrichmentItemId and relativeEnrichmentItemId):
                raise ValueError(
                    "Must supply exactly one between 'relativeMediaItemId' and 'relativeEnrichmentItemId'")
            if relativeMediaItemId:
                self.relativeMediaItemId = relativeMediaItemId
            else:
                self.relativeEnrichmentItemId = relativeEnrichmentItemId

    def to_dict(self) -> dict:
        dct: dict = self.__dict__.copy()
        dct["position"] = self.position.value
        return dct


class MediaItemResult(Printable):
    @staticmethod
    def from_dict(gp: "gp_wrapper.GooglePhotos", dct: dict) -> "MediaItemResult":
        return MediaItemResult(
            mediaItem=gp_wrapper.MediaItem(
                gp, **dct["mediaItem"]),
            status=dct["status"] if "status" in dct else None,
            uploadToken=dct["uploadToken"] if "uploadToken" in dct else None,
        )
    def __init__(self, mediaItem: "gp_wrapper.MediaItem", status: Optional[dict[str, str]] = None,
                 uploadToken: Optional[str] = None) -> None:  # type:ignore
        self.uploadToken = uploadToken
        self.status = status
        self.mediaItem = mediaItem


class MediaMetadata(Dictable, Printable):
    @staticmethod
    def from_dict(dct: dict) -> "MediaMetadata":
        return MediaMetadata(**dct)

    def __init__(self, creationTime: str, width: str, height: str, photo: Optional[dict] = None) -> None:
        FORMAT = "%Y-%m-%dT%H:%M:%SZ"
        self.creationTime: datetime = datetime.strptime(creationTime, FORMAT)
        self.width: int = int(width)
        self.height: int = int(height)
        self.photo = photo

    def to_dict(self) -> dict:
        return json.loads(json.dumps(self.__dict__))


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
