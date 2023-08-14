from typing import Optional, Generator, Iterable
from requests.models import Response

from gp_wrapper.objects.core.album import CoreGPAlbum
from gp_wrapper.objects.core.gp import CoreGooglePhotos
from .core import CoreGooglePhotos, CoreGPAlbum, CoreEnrichmentItem
from .MediaItem import GPMediaItem
from ..utils import NextPageToken, PositionType, EnrichmentType, RequestType, AlbumMaskType


class GPAlbum(CoreGPAlbum):
    # ================================= HELPER STATIC METHODS =================================
    @staticmethod
    def _from_core(obj: CoreGPAlbum) -> "GPAlbum":
        return GPAlbum(**obj.__dict__)

    # ================================= OVERRIDDEN STATIC METHODS =================================
    @staticmethod
    def get(gp: CoreGooglePhotos, albumId: str) -> Optional["GPAlbum"]:
        core = CoreGPAlbum.get(gp, albumId)
        if not core:
            return None
        return GPAlbum._from_core(core)

    @staticmethod
    def create(gp: CoreGooglePhotos, album_name: str) -> "GPAlbum":
        return GPAlbum._from_core(CoreGPAlbum.create(gp, album_name))

    # ================================= ADDITIONAL STATIC METHODS =================================

    @staticmethod
    def all_albums(
        gp: CoreGooglePhotos,
        pageSize: int = 20,
        prevPageToken: Optional[NextPageToken] = None,
        excludeNonAppCreatedData: bool = False
    ) -> Generator["GPAlbum", None, None]:
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
        gen, prevPageToken = GPAlbum.list(
            gp, pageSize, None, excludeNonAppCreatedData)
        yield from (GPAlbum._from_core(g) for g in gen)
        while prevPageToken:
            gen, prevPageToken = GPAlbum.list(
                gp, pageSize, prevPageToken, excludeNonAppCreatedData)
            yield from (GPAlbum._from_core(g) for g in gen)

    @staticmethod
    def exists(gp: CoreGooglePhotos, /, name: Optional[str] = None, id: Optional[str] = None) -> Optional["GPAlbum"]:
        """checks whether an album exists, if so - returns it

        *supply only one
        Args:
            name (Optional[str]): supply a name to get first album with this name [NOT EFFICIENT]
            id (Optional[str]): supply id to get album with this exact id [EFFICIENT]
        Raises:
            ValueError: if both identifiers are used

        Returns:
             Optional[GPAlbum]: returns the album if it exists or None
        """
        if id is not None and name is not None:
            raise ValueError("must use only one between 'id' and 'name'")
        if id is not None:
            core = GPAlbum.get(gp, id)
            if core:
                return core
            return None
        for album in GPAlbum.all_albums(gp):
            if name:
                if album.title == name:
                    return album
        return None

    @staticmethod
    def from_dict(gp: CoreGooglePhotos, dct: dict) -> "GPAlbum":
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

    # ================================= ADDITIONAL INSTANCE METHODS =================================
    def add_text(self, description_parts: Iterable[str],
                 relative_position: PositionType = PositionType.FIRST_IN_ALBUM,
                 optional_additional_data: Optional[dict] = None) \
            -> Iterable[tuple[Optional[Response], Optional[CoreEnrichmentItem]]]:
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

    def set_title(self, new_title: str) -> Response:
        """sets the title of an album

        Args:
            new_title (str): new title to set to

        Returns:
            Response: response of this request
        """
        res = self.patch(AlbumMaskType.TITLE, new_title)
        if res.status_code == 200:
            self.title = new_title
        return res


__all__ = [
    "GPAlbum",
    "PositionType",
    "EnrichmentType"
]
