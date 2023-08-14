from typing import Optional, Iterable
from requests.models import Response
from .gp import CoreGooglePhotos
from .media_item import MediaItemID, CoreGPMediaItem
from .enrichment_item import CoreEnrichmentItem
from ...utils import AlbumId, Path, PositionType, EnrichmentType, RequestType, ALBUMS_ENDPOINT, Printable


class CoreGPAlbum(Printable):
    """A wrapper class over Album object
    """
    @staticmethod
    def _from_dict(gp: CoreGooglePhotos, dct: dict) -> "CoreGPAlbum":
        """creates a GooglePhotosAlbum object from a dict from a response object

        Args:
            gp (gp_wrapper.gp.GooglePhotos): the GooglePhotos object
            dct (dict): the dict object containing the data

        Returns:
            GooglePhotosAlbum: the resulting object
        """
        return CoreGPAlbum(
            gp,
            id=dct["id"],
            title=dct["title"],
            productUrl=dct["productUrl"],
            isWriteable=dct["isWriteable"],
            mediaItemsCount=int(dct["mediaItemsCount"]
                                ) if "mediaItemsCount" in dct else 0,
            coverPhotoBaseUrl=dct["coverPhotoBaseUrl"] if "coverPhotoBaseUrl" in dct else "",
            coverPhotoMediaItemId=dct["coverPhotoMediaItemId"] if "coverPhotoMediaItemId" in dct else "",
        )

    def __init__(self, gp: CoreGooglePhotos, id: AlbumId, title: str, productUrl: str, isWriteable: bool,
                 mediaItemsCount: int, coverPhotoBaseUrl: str, coverPhotoMediaItemId: MediaItemID):
        self.gp = gp
        self.id = id
        self.title = title
        self.productUrl = productUrl
        self.isWriteable = isWriteable
        self.mediaItemsCount = mediaItemsCount
        self.coverPhotoBaseUrl = coverPhotoBaseUrl
        self.coverPhotoMediaItemId = coverPhotoMediaItemId

    def addEnrichment(self, enrichment_type: EnrichmentType, enrichment_data: dict,
                      album_position: PositionType, album_position_data: Optional[dict] = None)\
            -> tuple[Optional[Response], Optional[CoreEnrichmentItem]]:
        """Adds an enrichment at a specified position in a defined album.

        Args:
            enrichment_type (EnrichmentType): the type of the enrichment
            enrichment_data (dict): the data for the enrichment
            album_position (ALbumPosition): where to add the enrichment
            album_position_data (Optional[dict], optional): additional data maybe required for some of the options.
                Defaults to None.

        Returns:
            EnrichmentItem: the item added
        """
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

        response = self.gp.request(RequestType.POST, endpoint, json=body)
        try:
            return None, CoreEnrichmentItem(response.json()["enrichmentItem"]["id"])
        except:
            return response, None

    def batchAddMediaItems(self, paths: Iterable[Path]) -> tuple[Iterable[Response], Iterable[CoreGPMediaItem]]:
        """Adds one or more media items in a user's Google Photos library to an album.

        Args:
            paths (Iterable[Path]): paths to media files

        Returns:
            tuple[Iterable[Response], Iterable[GooglePhotosMediaItem]]: responses per batch request.
                the individual media items.
        """
        pass

    def batchRemoveMediaItems(self): ...

    @staticmethod
    def create(gp: CoreGooglePhotos, album_name: str) -> "CoreGPAlbum":
        payload = {
            "album": {
                "title": album_name
            }
        }
        response = gp.request(
            RequestType.POST,
            ALBUMS_ENDPOINT,
            json=payload,
        )
        dct = response.json()
        album = CoreGPAlbum._from_dict(gp, dct)
        return album

    @staticmethod
    def get(gp: CoreGooglePhotos) -> "CoreGPAlbum": ...

    @staticmethod
    def list(gp: CoreGooglePhotos) -> Iterable["CoreGPAlbum"]: ...

    def patch(self): ...

    def share(self, isCollaborative: bool = True, isCommentable: bool = True) -> Response:
        """share an album

        Args:
            isCollaborative (bool, optional): whether to allow other people to also edit the album. Defaults to True.
            isCommentable (bool, optional): whether to allow other people to comment. Defaults to True.

        Returns:
            Response: _description_
        """
        endpoint = f"https://photoslibrary.googleapis.com/v1/albums/{self.id}:addEnrichment"
        body = {
            "sharedAlbumOptions": {
                "isCollaborative": isCollaborative,
                "isCommentable": isCommentable
            }
        }
        response = self.gp.request(
            RequestType.POST, endpoint, json=body)
        return response

    def unshare(self) -> Response:
        """make a shared album private

        Returns:
            Response: resulting response
        """
        endpoint = f"https://photoslibrary.googleapis.com/v1/albums/{self.id}:unshare"
        response = self.gp.request(
            RequestType.POST, endpoint, use_json_headers=False)
        return response
