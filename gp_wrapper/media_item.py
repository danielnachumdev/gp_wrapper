import json
import gp_wrapper.gp  # pylint: disable=unused-import
from .utils import MediaItemID, json_default


class GooglePhotosMediaItem:
    """A wrapper class over Media Item object
    """

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

    def set_description(self, description: str):
        endpoint = f"https://photoslibrary.googleapis.com/v1/mediaItems/{self.id}"
        headers = self.gp._construct_headers(
            {"Content-Type": "application/json"})
        body = {
            "description": description
        }
        response = self.gp.post(endpoint, json=body, headers=headers)
        print(response.json())
        return response

    def update(self):
        endpoint = f"https://photoslibrary.googleapis.com/v1/mediaItems/{self.id}"
        update_mask = "user.displayName,photo"


__all__ = [
    "GooglePhotosMediaItem"
]
