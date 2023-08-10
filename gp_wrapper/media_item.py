import json
import enum
from requests.models import Response
import gp_wrapper.gp  # pylint: disable=unused-import
from .utils import MediaItemID, json_default, declare, MaskTypes, RequestType


class GooglePhotosMediaItem:
    """A wrapper class over Media Item object
    """
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

    @declare("Setting MediaItem's description")
    def set_description(self, description: str) -> Response:
        return self._update(MaskTypes.DESCRIPTION, description)

    @declare("Updating MediaItem")
    def _update(self, field_name: MaskTypes, field_value: str) -> Response:
        endpoint = f"https://photoslibrary.googleapis.com/v1/mediaItems/{self.id}"
        headers = self.gp.json_headers()
        body = {
            field_name.value: field_value
        }
        params = {
            "updateMask": field_name.value
        }
        response = self.gp.request(
            RequestType.PATCH, endpoint, json=body, headers=headers, params=params)
        return response


__all__ = [
    "GooglePhotosMediaItem",
    "MaskTypes"
]
