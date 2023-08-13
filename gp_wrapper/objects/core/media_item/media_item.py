from typing import Iterable, Optional, Union, Generator
from requests.models import Response
from .filters import SearchFilter
import gp_wrapper.objects.core.gp  # pylint: disable=unused-import
from ....utils import MaskTypes, RequestType, AlbumPosition, NewMediaItem,\
    MediaItemResult, MediaMetadata, Printable
from ....utils import MediaItemID, AlbumId, Path, NextPageToken
from ....utils import UPLOAD_MEDIA_ITEM_ENDPOINT, MEDIA_ITEMS_CREATE_ENDPOINT
from ....utils import slowdown


class CoreGPMediaItem(Printable):
    """A wrapper class over Media Item object
    """
    @staticmethod
    @slowdown(2)
    def upload_media(gp: "gp_wrapper.objects.core.gp.CoreGooglePhotos", media: Path) -> str:
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
            gp: "gp_wrapper.objects.core.gp.CoreGooglePhotos", newMediaItems: Iterable[NewMediaItem], albumId: Optional[AlbumId] = None,
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
    def batchGet(gp: "gp_wrapper.objects.core.gp.CoreGooglePhotos", ids: Iterable[str]
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
    def get(gp: "gp_wrapper.objects.core.gp.CoreGooglePhotos", mediaItemId: str) -> Response:
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
        return response  # GPMediaItem.from_dict(gp, response.json())

    @staticmethod
    def search(
            gp: "gp_wrapper.objects.core.gp.CoreGooglePhotos",
            albumId: Optional[str] = None,
            pageSize: int = 25,
            pageToken: Optional[str] = None,
            filters: Optional[SearchFilter] = None,
            orderBy: Optional[str] = None
    ) -> tuple[list[dict], Optional[NextPageToken]]:
        """_summary_

        Raises:
            ValueError: _description_
        """
        if not (0 < pageSize <= 100):
            raise ValueError(
                "pageSize must be a positive integer. maximum value: 100")
        endpoint = "https://photoslibrary.googleapis.com/v1/mediaItems:search"
        payload: dict = {
            "pageSize": pageSize
        }

        if albumId:
            payload["albumId"] = albumId

        if pageToken:
            payload["pageToken"] = pageToken

        if filters:
            payload["filters"] = {}
            if filters.contentFilter:
                pass

            if filters.dateFilter:
                payload["filters"]["dateFilter"] = filters.dateFilter.to_dict()

            if filters.featureFilter:
                pass

            if filters.mediaTypeFilter:
                pass
            payload["filters"] = None  # TODO

        if orderBy:
            if not filters or not filters.dateFilter:
                raise ValueError(
                    "The orderBy field only works when a dateFilter is used.")
            payload["orderBy"] = None  # TODO

        response = gp.request(RequestType.POST, endpoint, json=payload)
        response.raise_for_status()
        j = response.json()
        mediaItems = j["mediaItems"] if "mediaItems" in j else []
        nextPageToken = j["nextPageToken"] if "nextPageToken" in j else None
        # (GPMediaItem.from_dict(gp, dct) for dct in mediaItems), nextPageToken
        return mediaItems, nextPageToken

    @staticmethod
    def list(gp: "gp_wrapper.objects.core.gp.CoreGooglePhotos", pageSize: int = 25,
             pageToken: Optional[str] = None) -> tuple[list[dict], Optional[NextPageToken]]:
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
        # (GPMediaItem.from_dict(gp, dct) for dct in mediaItems), nextPageToken
        return mediaItems, nextPageToken

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

    def __init__(self, gp: "gp_wrapper.objects.core.gp.CoreGooglePhotos", id: MediaItemID, productUrl: str,
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


__all__ = [
    "CoreGPMediaItem"
]