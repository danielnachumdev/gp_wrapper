from requests.models import Response
from .core import CoreGooglePhotos, CoreGPMediaItem
from ..utils import MaskTypes


class GPMediaItem(CoreGPMediaItem):
    @staticmethod
    def _from_core(c: CoreGPMediaItem) -> "GPMediaItem":
        return GPMediaItem(**c.__dict__)

    @staticmethod
    def from_dict(gp: CoreGooglePhotos, dct: dict) -> "GPMediaItem":
        return GPMediaItem._from_core(GPMediaItem._from_dict(gp, dct))

    def set_description(self, description: str) -> Response:
        return self.patch(MaskTypes.DESCRIPTION, description)


__all__ = [
    "GPMediaItem",
    "MaskTypes"
]
