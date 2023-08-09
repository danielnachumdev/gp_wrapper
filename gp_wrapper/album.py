import json
import enum
from typing import Optional, Generator, Iterable
from requests import Response
import gp_wrapper.gp  # pylint: disable=unused-import
from .media_item import MediaItemID, GooglePhotosMediaItem
from .utils import AlbumId, Path, declare, json_default
from .enrichment_item import EnrichmentItem


class ALbumPosition(enum.Enum):
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


class GooglePhotosAlbum:
    """A wrapper class over Album object
    """
    @staticmethod
    @declare("Creating album from id")
    def from_id(gp: "gp_wrapper.gp.GooglePhotos", album_id: AlbumId) -> Optional["GooglePhotosAlbum"]:
        """will return the album with the specified id if it exists
        """
        for album in gp.get_albums():
            if album.id == album_id:
                return album
        return None

    @staticmethod
    @declare("Creating album from name")
    def from_name(gp: "gp_wrapper.gp.GooglePhotos", album_name: str, create_on_missing: bool = False) -> Generator["GooglePhotosAlbum", None, None]:
        'will return all albums with the specified name'
        has_yielded: bool = False
        for album in gp.get_albums():
            if album.title == album_name:
                has_yielded = True
                yield album

        if create_on_missing:
            if not has_yielded:
                yield gp.create_album(album_name)

        return

    def __init__(self, gp: "gp_wrapper.gp.GooglePhotos", id: AlbumId, title: str, productUrl: str, isWriteable: bool,
                 mediaItemsCount: int, coverPhotoBaseUrl: str, coverPhotoMediaItemId: MediaItemID):
        self.gp = gp
        self.id = id
        self.title = title
        self.productUrl = productUrl
        self.isWriteable = isWriteable
        self.mediaItemsCount = mediaItemsCount
        self.coverPhotoBaseUrl = coverPhotoBaseUrl
        self.coverPhotoMediaItemId = coverPhotoMediaItemId

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {json.dumps(self.__dict__, indent=4,default=json_default)}"

    @declare("Adding media to album")
    def add_media(self, paths: Iterable[Path]) -> Iterable[Response]:
        return self.gp.upload_media_batch(self, paths)

    @declare("Adding an enrichment to an Album")
    def add_enrichment(self, enrichment_type: EnrichmentType, enrichment_data: dict, album_position: ALbumPosition, album_position_data: Optional[dict] = None) -> EnrichmentItem:
        endpoint = f"https://photoslibrary.googleapis.com/v1/albums/{self.id}:addEnrichment"
        body: dict[str, dict] = {
            "newEnrichmentItem": {
                enrichment_type.value: enrichment_data
            },
            "albumPosition": {
                "position": album_position.value
            }
        }
        if album_position_data is not None:
            body["albumPosition"].update(album_position_data)

        headers = self.gp._construct_headers(
            {"Content-Type": "application/json"})
        response = self.gp.post(endpoint, json=body, headers=headers)
        return EnrichmentItem(response.json()["enrichmentItem"]["id"])

    @declare("Adding description to album")
    def add_description(self, description: str, relative_position: ALbumPosition = ALbumPosition.FIRST_IN_ALBUM) -> EnrichmentItem:
        return self.add_enrichment(
            EnrichmentType.TEXT_ENRICHMENT,
            {"text": description},
            relative_position
        )

    @declare("Sharing an album")
    def share(self, isCollaborative: bool = True, isCommentable: bool = True) -> Response:
        endpoint = f"https://photoslibrary.googleapis.com/v1/albums/{self.id}:addEnrichment"
        body = {
            "sharedAlbumOptions": {
                "isCollaborative": isCollaborative,
                "isCommentable": isCommentable
            }
        }
        response = self.gp.post(endpoint, json=body,
                                headers=self.gp.json_headers())
        return response

    @declare("Un-sharing an album")
    def unshare(self) -> Response:
        endpoint = f"https://photoslibrary.googleapis.com/v1/albums/{self.id}:unshare"
        response = self.gp.post(endpoint, headers=self.gp._construct_headers())
        return response

    @declare("Getting media in album")
    def get_media(self) -> Iterable[GooglePhotosMediaItem]:
        endpoint = "https://photoslibrary.googleapis.com/v1/mediaItems:search"
        data = {
            "albumId": self.id
        }
        response = self.gp.post(
            endpoint, headers=self.gp.json_headers(), json=data)
        if not response.status_code == 200:
            return []
        j = response.json()
        if "mediaItems" not in j:
            return []
        for dct in j["mediaItems"]:
            yield GooglePhotosMediaItem(
                self.gp,
                id=dct["id"],
                productUrl=dct["productUrl"],
                baseUrl=dct["baseUrl"],
                mimeType=dct["mimeType"],
                mediaMetadata=dct["mediaMetadata"],
                filename=dct["filename"],
            )


__all__ = [
    "GooglePhotosAlbum",
    "ALbumPosition",
    "EnrichmentType"
]
