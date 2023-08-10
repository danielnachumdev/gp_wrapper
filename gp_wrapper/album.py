from typing import Optional, Generator, Iterable
from requests.models import Response
import gp_wrapper.gp  # pylint: disable=unused-import
from .media_item import MediaItemID, GPMediaItem
from .structures import AlbumId, Path, NextPageToken,\
    PositionType, EnrichmentType, RequestType, ALBUMS_ENDPOINT, Printable
from .enrichment_item import EnrichmentItem


DEFAULT_PAGE_SIZE: int = 20


class _GPAlbum(Printable):
    """A wrapper class over Album object
    """

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

    def addEnrichment(self, enrichment_type: EnrichmentType, enrichment_data: dict,
                      album_position: PositionType, album_position_data: Optional[dict] = None)\
            -> tuple[Optional[Response], Optional[EnrichmentItem]]:
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
            return None, EnrichmentItem(response.json()["enrichmentItem"]["id"])
        except:
            return response, None

    def batchAddMediaItems(self, paths: Iterable[Path]) -> tuple[Iterable[Response], Iterable[GPMediaItem]]:
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
    def create(gp: "gp_wrapper.gp.GooglePhotos", album_name: str) -> "GPAlbum":
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
        album = GPAlbum.from_dict(gp, dct)
        return album

    @staticmethod
    def get(gp: "gp_wrapper.gp.GooglePhotos") -> "GPAlbum": ...

    @staticmethod
    def list(
        gp: "gp_wrapper.gp.GooglePhotos") -> Iterable["GPAlbum"]: ...

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


class GPAlbum(_GPAlbum):
    @staticmethod
    def _get_albums_helper(gp: "gp_wrapper.gp.GooglePhotos"):
        endpoint = "https://photoslibrary.googleapis.com/v1/albums"
        # body: dict[str, str | int] = {
        #     # "pageSize": page_size,
        #     # "excludeNonAppCreatedData": excludeNonAppCreatedData
        # }
        # if prevPageToken is not None:
        #     body["pageToken"] = prevPageToken
        response = gp.request(RequestType.GET, endpoint,
                              use_json_headers=False)
        j = response.json()
        if "albums" not in j:
            # TODO
            return ""
        for dct in j["albums"]:
            yield GPAlbum.from_dict(gp, dct)
        return j["nextPageToken"]

    @staticmethod
    def all_albums(gp: "gp_wrapper.gp.GooglePhotos", page_size: int = DEFAULT_PAGE_SIZE,
                       prevPageToken: Optional[NextPageToken] = None, excludeNonAppCreatedData: bool = False)\
            -> Generator["GPAlbum", None, Optional[NextPageToken]]:
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
        response = gp.request(RequestType.GET, endpoint,
                              use_json_headers=False)
        j = response.json()
        if "albums" not in j:
            return None
        for dct in j["albums"]:
            yield GPAlbum.from_dict(gp, dct)
        if "nextPageToken" in j:
            return j["nextPageToken"]
        return None

    @staticmethod
    def from_dict(gp: "gp_wrapper.gp.GooglePhotos", dct: dict) -> "GPAlbum":
        """creates a GooglePhotosAlbum object from a dict from a response object

        Args:
            gp (gp_wrapper.gp.GooglePhotos): the GooglePhotos object
            dct (dict): the dict object containing the data

        Returns:
            GooglePhotosAlbum: the resulting object
        """
        return GPAlbum(
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

    @staticmethod
    def from_id(gp: "gp_wrapper.gp.GooglePhotos", album_id: AlbumId) -> Optional["GPAlbum"]:
        """will return the album with the specified id if it exists
        """
        endpoint = f"https://photoslibrary.googleapis.com/v1/albums/{album_id}"
        response = gp.request(RequestType.GET, endpoint,
                              use_json_headers=False)
        if response.status_code == 200:
            return GPAlbum.from_dict(gp, response.json())
        return None

    @staticmethod
    def from_name(gp: "gp_wrapper.gp.GooglePhotos", album_name: str, create_on_missing: bool = False)\
            -> Generator["GPAlbum", None, None]:
        'will return all albums with the specified name'
        has_yielded: bool = False
        for album in GPAlbum.all_albums(gp):
            if album.title == album_name:
                has_yielded = True
                yield album

        if create_on_missing:
            if not has_yielded:
                yield GPAlbum.create(gp, album_name)

        return

    def add_description(self, description_parts: Iterable[str],
                        relative_position: PositionType = PositionType.FIRST_IN_ALBUM,
                        optional_additional_data: Optional[dict] = None) \
            -> Iterable[tuple[Optional[Response], Optional[EnrichmentItem]]]:
        """a facade function that uses 'add_enrichment' to simplify adding a description

        Args:
            description (str): description to add
            relative_position (ALbumPosition, optional): where to add the description. 
                Defaults to ALbumPosition.FIRST_IN_ALBUM.

        Returns:
            EnrichmentItem: the resulting item
        """
        HARD_LIMIT: int = 1000
        # copy the items if it is a generator
        parts = list(description_parts)
        for part in parts:
            if len(part) > HARD_LIMIT:
                raise ValueError(
                    f"the description parts should be less than {HARD_LIMIT} characters"
                    "long because of a hard limit google employs")

        chunks: list[str] = []
        tmp_chunk = ""
        for text in parts:
            if len(tmp_chunk) + len(text) >= 1000:
                chunks.append(tmp_chunk)
                tmp_chunk = ""
            tmp_chunk += text

        if len(tmp_chunk) > 0:
            chunks.append(tmp_chunk)

        items = []
        for part in chunks[::-1]:
            items.append(self.addEnrichment(
                EnrichmentType.TEXT_ENRICHMENT,
                {"text": part},
                relative_position,
                album_position_data=optional_additional_data
            ))
        return items

    def get_media(self) -> Iterable[GPMediaItem]:
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
        response = self.gp.request(
            RequestType.POST, endpoint, json=data)
        if not response.status_code == 200:
            return []
        j = response.json()
        if "mediaItems" not in j:
            return []
        for dct in j["mediaItems"]:
            yield GPMediaItem.from_dict(self.gp, dct)

    @staticmethod
    def exists(gp: "gp_wrapper.gp.GooglePhotos", /, name: Optional[str] = None, id: Optional[str] = None) -> Optional["GPAlbum"]:
        for album in GPAlbum.all_albums(gp):
            if name:
                if album.title == name:
                    return album
            if id:
                if album.id == id:
                    return album

        return None


__all__ = [
    "GPAlbum",
    "PositionType",
    "EnrichmentType"
]
