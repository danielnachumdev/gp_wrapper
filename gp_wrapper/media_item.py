import json
from typing import Iterable, Optional, Union
from requests.models import Response
import gp_wrapper.gp  # pylint: disable=unused-import
from .structures import MediaItemID, MaskTypes, RequestType,\
    Path, UPLOAD_MEDIA_ITEM_ENDPOINT, AlbumId, AlbumPosition, NewMediaItem,\
    MEDIA_ITEMS_CREATE_ENDPOINT
from .helpers import json_default, slowdown


class _GooglePhotosMediaItem:
    """A wrapper class over Media Item object
    """
    @staticmethod
    @slowdown(2)
    def _upload_media(gp: "gp_wrapper.gp.GooglePhotos", media: Path) -> str:
        headers = gp._json_headers()
        image_data = open(media, 'rb').read()
        response = gp.request(
            RequestType.POST,
            UPLOAD_MEDIA_ITEM_ENDPOINT,
            data=image_data,
            headers=headers
        )
        token = response.content.decode('utf-8')
        return token

    @staticmethod
    def batchCreate(
            gp: "gp_wrapper.gp.GooglePhotos", newMediaItems: Iterable[NewMediaItem], albumId: Optional[AlbumId] = None,
                albumPosition: Optional[AlbumPosition] = None) \
            -> Iterable["GooglePhotosMediaItem"]:
        # TODO: If you are creating a media item in a shared album where you are not the owner, you are not allowed to position the media item. Doing so will result in a BAD REQUEST error.
        # see https://developers.google.com/photos/library/reference/rest/v1/mediaItems/batchCreate
        body: dict[str, Union[str, list, dict]] = {
            "newMediaItems": []
        }
        for media_item in newMediaItems:
            description, simple_media_item = media_item
            upload_token, file_name = simple_media_item
            item: dict = {
                # see https://developers.google.com/photos/library/reference/rest/v1/mediaItems/batchCreate#NewMediaItem
                "description": description,
                "simpleMediaItem": {
                    # see https://developers.google.com/photos/library/reference/rest/v1/mediaItems/batchCreate#SimpleMediaItem
                    "uploadToken": upload_token,
                    "fileName": file_name
                }
            }
            body["newMediaItems"].append(item)  # type:ignore
        if albumId and albumPosition:
            body["albumId"] = albumId
            body["albumPosition"] = albumPosition.to_dict()
        elif not albumId and not albumPosition:
            pass
        else:
            raise ValueError(
                "'albumId' and 'albumPosition' must be passed together")

        print(json.dumps(body, indent=4))
        # gp.request(RequestType.POST, MEDIA_ITEMS_CREATE_ENDPOINT, json=body)

    @staticmethod
    def batchGet(gp: "gp_wrapper.gp.GooglePhotos", ids: Iterable[str]
                 ) -> Iterable["GooglePhotosMediaItem"]: ...

    @staticmethod
    def get(gp: "gp_wrapper.gp.GooglePhotos") -> "GooglePhotosMediaItem": ...

    def patch(self): ...

    @staticmethod
    def search(
        gp: "gp_wrapper.gp.GooglePhotos") -> Iterable["GooglePhotosMediaItem"]: ...

    def __init__(self, gp: "gp_wrapper.gp.GooglePhotos", id: MediaItemID, productUrl: str,
                 mimeType: str, mediaMetadata: dict, filename: str, baseUrl: str = "") -> None:
        self.gp = gp
        self.id = id
        self.productUrl = productUrl
        self.mimeType = mimeType
        self.mediaMetadata = mediaMetadata
        self.filename = filename

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {json.dumps(self.__dict__, indent=4,default=json_default)}"


class GooglePhotosMediaItem(_GooglePhotosMediaItem):
    @staticmethod
    def from_dict(gp: "gp_wrapper.gp.GooglePhotos", dct: dict) -> "GooglePhotosMediaItem":
        return GooglePhotosMediaItem(
            gp,
            id=dct["id"],
            productUrl=dct["productUrl"],
            mimeType=dct["mimeType"],
            mediaMetadata=dct["mediaMetadata"],
            filename=dct["filename"],
        )

    def set_description(self, description: str) -> Response:
        return self._update(MaskTypes.DESCRIPTION, description)

    def _update(self, field_name: MaskTypes, field_value: str) -> Response:
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


__all__ = [
    "GooglePhotosMediaItem",
    "MaskTypes"
]
