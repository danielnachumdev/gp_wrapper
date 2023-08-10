from typing import Iterable, Optional, Union, Generator
from requests.models import Response
import gp_wrapper.gp  # pylint: disable=unused-import
from .structures import MaskTypes, RequestType, AlbumPosition, NewMediaItem,\
    MediaItemResult, MediaMetadata, Printable
from .structures import MediaItemID, AlbumId, Path, NextPageToken
from .structures import UPLOAD_MEDIA_ITEM_ENDPOINT, MEDIA_ITEMS_CREATE_ENDPOINT
from .helpers import slowdown


class _GPMediaItem(Printable):
    """A wrapper class over Media Item object
    """
    @staticmethod
    @slowdown(2)
    def upload_media(gp: "gp_wrapper.gp.GooglePhotos", media: Path) -> str:
        image_data = open(media, 'rb').read()
        response = gp.request(
            RequestType.POST,
            UPLOAD_MEDIA_ITEM_ENDPOINT,
            data=image_data,
        )
        token = response.content.decode('utf-8')
        return token

    @staticmethod
    def batchCreate(
            gp: "gp_wrapper.gp.GooglePhotos", newMediaItems: Iterable[NewMediaItem], albumId: Optional[AlbumId] = None,
                albumPosition: Optional[AlbumPosition] = None) \
            -> Generator[MediaItemResult, None, None]:
        """Creates one or more media items in a user's Google Photos library.
            This is the second step for creating a media item.\n
            For details regarding Step 1, uploading the raw bytes to a Google Server, see GPMediaItem.upload_media\n
            This call adds the media item to the library.
            If an album id is specified, the call adds the media item to the album too. 
            Each album can contain up to 20,000 media items. 
            By default, the media item will be added to the end of the library or album.
            If an album id and position are both defined, the media item is added to the album at the specified position.
            If the call contains multiple media items, they're added at the specified position. 
            If you are creating a media item in a shared album where you are not the owner, you are not allowed to position the media item.
            Doing so will result in a BAD REQUEST error.

        Raises:
            ValueError: If the optional arguments are passed incorrectly
            HTTPError: If the HTTP request has failed

        Yields:
            Generator[NewMediaItemResult, None, None]: A generator of wrapper objects representing the contents of the response
        """
        # TODO: If you are creating a media item in a shared album where you are not the owner, you are not allowed to position the media item. Doing so will result in a BAD REQUEST error.
        body: dict[str, Union[str, list, dict]] = {
            # see https://developers.google.com/photos/library/reference/rest/v1/mediaItems/batchCreate
            "newMediaItems": [item.to_dict() for item in newMediaItems]
        }
        if albumId and albumPosition:
            body["albumId"] = albumId
            body["albumPosition"] = albumPosition.to_dict()
        elif not albumId and not albumPosition:
            pass
        else:
            raise ValueError(
                "'albumId' and 'albumPosition' must be passed together")

        response = gp.request(
            RequestType.POST, MEDIA_ITEMS_CREATE_ENDPOINT, json=body)
        response.raise_for_status()
        for dct in response.json()["newMediaItemResults"]:
            yield MediaItemResult.from_dict(gp, dct)

    @staticmethod
    def batchGet(gp: "gp_wrapper.gp.GooglePhotos", ids: Iterable[str]
                 ) -> Generator[MediaItemResult, None, None]:
        """Returns the list of media items for the specified media item identifiers. Items are returned in the same order as the supplied identifiers.

        Returns:
            _type_: _description_
        """
        ENDPOINT = "https://photoslibrary.googleapis.com/v1/mediaItems:batchGet"
        params = {
            "mediaItemIds": ids
        }
        response = gp.request(RequestType.GET, ENDPOINT,
                              params=params, use_json_headers=False)
        response.raise_for_status()
        for dct in response.json()["mediaItemResults"]:
            yield MediaItemResult.from_dict(gp, dct)

    @staticmethod
    def get(gp: "gp_wrapper.gp.GooglePhotos", mediaItemId: str) -> "GPMediaItem":
        """Returns the media item for the specified media item identifier.

        Args:
            gp (gp_wrapper.gp.GooglePhotos): Google Photos object
            mediaItemId (str): the id of the wanted item
        Raises:
            HTTPError: if the request fails
        Returns:
            GPMediaItem: the resulting object
        """
        endpoint = f"https://photoslibrary.googleapis.com/v1/mediaItems/{mediaItemId}"
        response = gp.request(RequestType.GET, endpoint)
        response.raise_for_status()
        return GPMediaItem.from_dict(gp, response.json())

    @staticmethod
    def list(gp: "gp_wrapper.gp.GooglePhotos", pageSize: int = 25,
             pageToken: Optional[str] = None) -> tuple[Generator["GPMediaItem", None, None], Optional[NextPageToken]]:
        if not (0 < pageSize <= 100):
            raise ValueError(
                "pageSize must be between 0 and 100.\nsee https://developers.google.com/photos/library/reference/rest/v1/mediaItems/list#query-parameters")
        endpoint = "https://photoslibrary.googleapis.com/v1/mediaItems"
        params: dict = {
            "pageSize": pageSize
        }
        if pageToken:
            params["pageToken"] = pageToken
        response = gp.request(RequestType.GET, endpoint,
                              params=params, use_json_headers=False)
        response.raise_for_status()
        j = response.json()
        mediaItems = j["mediaItems"] if "mediaItems" in j else []
        nextPageToken = j["nextPageToken"] if "nextPageToken" in j else None
        return (GPMediaItem.from_dict(gp, dct) for dct in mediaItems), nextPageToken

    def patch(self, field_name: MaskTypes, field_value: str) -> Response:
        endpoint = f"https://photoslibrary.googleapis.com/v1/mediaItems/{self.id}"
        payload = {
            field_name.value: field_value
        }
        params = {
            "updateMask": field_name.value
        }
        response = self.gp.request(
            RequestType.PATCH, endpoint, json=payload, params=params)
        return response

    @staticmethod
    def search(
            gp: "gp_wrapper.gp.GooglePhotos") -> Iterable["GPMediaItem"]:
        endpoint = "https://photoslibrary.googleapis.com/v1/mediaItems:search"
        response = gp.request(RequestType.POST, endpoint)
        response.raise_for_status()

    def __init__(self, gp: "gp_wrapper.gp.GooglePhotos", id: MediaItemID, productUrl: str,
                 mimeType: str, mediaMetadata: dict | MediaMetadata, filename: str, baseUrl: str = "", description: str = "") -> None:
        self.gp = gp
        self.id = id
        self.productUrl = productUrl
        self.mimeType = mimeType
        self.mediaMetadata: MediaMetadata = mediaMetadata if isinstance(
            mediaMetadata, MediaMetadata) else MediaMetadata.from_dict(mediaMetadata)
        self.filename = filename
        self.baseUrl = baseUrl
        self.description = description


class GPMediaItem(_GPMediaItem):
    @staticmethod
    def from_dict(gp: "gp_wrapper.gp.GooglePhotos", dct: dict) -> "GPMediaItem":
        return GPMediaItem(
            gp,
            id=dct["id"],
            productUrl=dct["productUrl"],
            mimeType=dct["mimeType"],
            mediaMetadata=MediaMetadata.from_dict(dct["mediaMetadata"]),
            filename=dct["filename"],
        )

    def set_description(self, description: str) -> Response:
        return self.patch(MaskTypes.DESCRIPTION, description)


__all__ = [
    "GPMediaItem",
    "MaskTypes"
]
