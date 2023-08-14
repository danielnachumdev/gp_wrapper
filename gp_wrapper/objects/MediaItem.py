# from typing import Iterable, Optional, Union, Generator
# from requests.models import Response
# import gp_wrapper.objects.core.gp  # pylint: disable=unused-import
# from ..utils import MaskTypes, RequestType, AlbumPosition, NewMediaItem,\
#     MediaItemResult, MediaMetadata, Printable
# from ..utils import MediaItemID, AlbumId, Path, NextPageToken
# from ..utils import UPLOAD_MEDIA_ITEM_ENDPOINT, MEDIA_ITEMS_CREATE_ENDPOINT
# from ..utils import slowdown


# class GPMediaItem(_GPMediaItem):
#     @staticmethod
#     def from_dict(gp: "gp_wrapper.gp.GooglePhotos", dct: dict) -> "GPMediaItem":
#         return GPMediaItem(
#             gp,
#             id=dct["id"],
#             productUrl=dct["productUrl"],
#             mimeType=dct["mimeType"],
#             mediaMetadata=MediaMetadata.from_dict(dct["mediaMetadata"]),
#             filename=dct["filename"],
#         )

#     def set_description(self, description: str) -> Response:
#         return self.patch(MaskTypes.DESCRIPTION, description)


# __all__ = [
#     "GPMediaItem",
#     "MaskTypes"
# ]
