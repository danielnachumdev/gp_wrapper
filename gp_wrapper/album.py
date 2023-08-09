import json
import enum
from typing import Optional, Generator, Iterable
from requests import Response
import gp_wrapper.gp  # pylint: disable=unused-import
from .media_item import MediaItemID, GooglePhotosMediaItem
from .utils import AlbumId, Path, declare, json_default, NextPageToken
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


DEFAULT_PAGE_SIZE: int = 20


class GooglePhotosAlbum:
    """A wrapper class over Album object
    """
    @staticmethod
    @declare("Getting albums")
    def get_albums(gp: "gp_wrapper.gp.GooglePhotos", page_size: int = DEFAULT_PAGE_SIZE,
                       prevPageToken: Optional[NextPageToken] = None, excludeNonAppCreatedData: bool = False)\
            -> Generator["GooglePhotosAlbum", None, NextPageToken]:
        """gets all albums serially

        pageSize (int): Maximum number of albums to return in the response.
            Fewer albums might be returned than the specified number. The default pageSize is 20, the maximum is 50.
        pageToken (str): A continuation token to get the next page of the results.
            Adding this to the request returns the rows after the pageToken.
            The pageToken should be the value returned in the nextPageToken parameter in the response
            to the listAlbums request.
        excludeNonAppCreatedData (bool): If set, the results exclude media items that were not created by this app.
            Defaults to false (all albums are returned).
            This field is ignored if the photoslibrary.readonly.appcreateddata scope is used.

        Returns:
            NextPageToken: a token to supply to a future call to get albums after current end point in album list

        Yields:
            GooglePhotosAlbum: yields the albums one after the other
        """
        endpoint = "https://photoslibrary.googleapis.com/v1/albums"
        # body: dict[str, str | int] = {
        #     # "pageSize": page_size,
        #     # "excludeNonAppCreatedData": excludeNonAppCreatedData
        # }
        # if prevPageToken is not None:
        #     body["pageToken"] = prevPageToken
        response = gp.get(endpoint,  headers=gp._construct_headers())
        j = response.json()
        for dct in j["albums"]:
            yield GooglePhotosAlbum.from_dict(gp, dct)
        return j["nextPageToken"]

    @staticmethod
    def from_dict(gp: "gp_wrapper.gp.GooglePhotos", dct: dict) -> "GooglePhotosAlbum":
        """creates a GooglePhotosAlbum object from a dict from a response object

        Args:
            gp (gp_wrapper.gp.GooglePhotos): the GooglePhotos object
            dct (dict): the dict object containing the data

        Returns:
            GooglePhotosAlbum: the resulting object
        """
        return GooglePhotosAlbum(
            gp,
            id=dct["id"],
            title=dct["title"],
            productUrl=dct["productUrl"],
            isWriteable=dct["isWriteable"],
            mediaItemsCount=dct["mediaItemsCount"] if "mediaItemsCount" in dct else 0,
            coverPhotoBaseUrl=dct["coverPhotoBaseUrl"] if "coverPhotoBaseUrl" in dct else "",
            coverPhotoMediaItemId=dct["coverPhotoMediaItemId"] if "coverPhotoMediaItemId" in dct else "",
        )

    @staticmethod
    @declare("Creating album from id")
    def from_id(gp: "gp_wrapper.gp.GooglePhotos", album_id: AlbumId) -> Optional["GooglePhotosAlbum"]:
        """will return the album with the specified id if it exists
        """
        endpoint = f"https://photoslibrary.googleapis.com/v1/albums/{album_id}"
        response = gp.get(endpoint, headers=gp._construct_headers())
        if response.status_code == 200:
            return GooglePhotosAlbum.from_dict(gp, response.json())
        return None

    @staticmethod
    @declare("Creating album from name")
    def from_name(gp: "gp_wrapper.gp.GooglePhotos", album_name: str, create_on_missing: bool = False)\
            -> Generator["GooglePhotosAlbum", None, None]:
        'will return all albums with the specified name'
        has_yielded: bool = False
        for album in GooglePhotosAlbum.get_albums(gp):
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
    def add_media(self, paths: Iterable[Path]) -> tuple[Iterable[Response], Iterable[GooglePhotosMediaItem]]:
        """a function to add media to the album

        Args:
            paths (Iterable[Path]): paths to media files

        Returns:
            tuple[Iterable[Response], Iterable[GooglePhotosMediaItem]]: responses per batch request.
                the individual media items.
        """
        return self.gp.upload_media_batch(self, paths)

    @declare("Adding an enrichment to an Album")
    def add_enrichment(self, enrichment_type: EnrichmentType, enrichment_data: dict,
                       album_position: ALbumPosition, album_position_data: Optional[dict] = None) -> EnrichmentItem:
        """A generic function to add an enrichment to an album

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

        headers = self.gp._construct_headers(
            {"Content-Type": "application/json"})
        response = self.gp.post(endpoint, json=body, headers=headers)
        return EnrichmentItem(response.json()["enrichmentItem"]["id"])

    @declare("Adding description to album")
    def add_description(self, description: str, relative_position: ALbumPosition = ALbumPosition.FIRST_IN_ALBUM) \
            -> EnrichmentItem:
        """a facade function that uses 'add_enrichment' to simplify adding a description

        Args:
            description (str): description to add
            relative_position (ALbumPosition, optional): where to add the description. 
                Defaults to ALbumPosition.FIRST_IN_ALBUM.

        Returns:
            EnrichmentItem: the resulting item
        """
        return self.add_enrichment(
            EnrichmentType.TEXT_ENRICHMENT,
            {"text": description},
            relative_position
        )

    @declare("Sharing an album")
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
        response = self.gp.post(endpoint, json=body,
                                headers=self.gp.json_headers())
        return response

    @declare("Un-sharing an album")
    def unshare(self) -> Response:
        """make a shared album private

        Returns:
            Response: resulting response
        """
        endpoint = f"https://photoslibrary.googleapis.com/v1/albums/{self.id}:unshare"
        response = self.gp.post(endpoint, headers=self.gp._construct_headers())
        return response

    @declare("Getting media in album")
    def get_media(self) -> Iterable[GooglePhotosMediaItem]:
        """gets all media in album

        Returns:
            Iterable[GooglePhotosMediaItem]: all media of the album

        Yields:
            Iterator[Iterable[GooglePhotosMediaItem]]: _description_
        """
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
