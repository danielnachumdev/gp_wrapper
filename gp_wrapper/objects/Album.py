# from typing import Optional, Generator, Iterable
# from requests.models import Response
# import gp_wrapper.objects.core.gp  # pylint: disable=unused-import
# from .MediaItem import MediaItemID, GPMediaItem
# from .core.enrichment_item import CoreEnrichmentItem
# from ..utils import AlbumId, Path, NextPageToken,\
#     PositionType, EnrichmentType, RequestType, ALBUMS_ENDPOINT, Printable


# DEFAULT_PAGE_SIZE: int = 20


# class GPAlbum(_GPAlbum):
#     @staticmethod
#     def _get_albums_helper(gp: "gp_wrapper.gp.GooglePhotos"):
#         endpoint = "https://photoslibrary.googleapis.com/v1/albums"
#         # body: dict[str, str | int] = {
#         #     # "pageSize": page_size,
#         #     # "excludeNonAppCreatedData": excludeNonAppCreatedData
#         # }
#         # if prevPageToken is not None:
#         #     body["pageToken"] = prevPageToken
#         response = gp.request(RequestType.GET, endpoint,
#                               use_json_headers=False)
#         j = response.json()
#         if "albums" not in j:
#             # TODO
#             return ""
#         for dct in j["albums"]:
#             yield GPAlbum.from_dict(gp, dct)
#         return j["nextPageToken"]

#     @staticmethod
#     def all_albums(gp: "gp_wrapper.gp.GooglePhotos", page_size: int = DEFAULT_PAGE_SIZE,
#                        prevPageToken: Optional[NextPageToken] = None, excludeNonAppCreatedData: bool = False)\
#             -> Generator["GPAlbum", None, Optional[NextPageToken]]:
#         """gets all albums serially

#         pageSize (int): Maximum number of albums to return in the response.
#             Fewer albums might be returned than the specified number. The default pageSize is 20, the maximum is 50.
#         pageToken (str): A continuation token to get the next page of the results.
#             Adding this to the request returns the rows after the pageToken.
#             The pageToken should be the value returned in the nextPageToken parameter in the response
#             to the listAlbums request.
#         excludeNonAppCreatedData (bool): If set, the results exclude media items that were not created by this app.
#             Defaults to false (all albums are returned).
#             This field is ignored if the photoslibrary.readonly.appcreateddata scope is used.

#         Returns:
#             NextPageToken: a token to supply to a future call to get albums after current end point in album list

#         Yields:
#             GooglePhotosAlbum: yields the albums one after the other
#         """
#         endpoint = "https://photoslibrary.googleapis.com/v1/albums"
#         # body: dict[str, str | int] = {
#         #     # "pageSize": page_size,
#         #     # "excludeNonAppCreatedData": excludeNonAppCreatedData
#         # }
#         # if prevPageToken is not None:
#         #     body["pageToken"] = prevPageToken
#         response = gp.request(RequestType.GET, endpoint,
#                               use_json_headers=False)
#         j = response.json()
#         if "albums" not in j:
#             return None
#         for dct in j["albums"]:
#             yield GPAlbum.from_dict(gp, dct)
#         if "nextPageToken" in j:
#             return j["nextPageToken"]
#         return None

#     @staticmethod
#     def from_dict(gp: "gp_wrapper.gp.GooglePhotos", dct: dict) -> "GPAlbum":
#         """creates a GooglePhotosAlbum object from a dict from a response object

#         Args:
#             gp (gp_wrapper.gp.GooglePhotos): the GooglePhotos object
#             dct (dict): the dict object containing the data

#         Returns:
#             GooglePhotosAlbum: the resulting object
#         """
#         return GPAlbum(
#             gp,
#             id=dct["id"],
#             title=dct["title"],
#             productUrl=dct["productUrl"],
#             isWriteable=dct["isWriteable"],
#             mediaItemsCount=int(dct["mediaItemsCount"]
#                                 ) if "mediaItemsCount" in dct else 0,
#             coverPhotoBaseUrl=dct["coverPhotoBaseUrl"] if "coverPhotoBaseUrl" in dct else "",
#             coverPhotoMediaItemId=dct["coverPhotoMediaItemId"] if "coverPhotoMediaItemId" in dct else "",
#         )

#     @staticmethod
#     def from_id(gp: "gp_wrapper.gp.GooglePhotos", album_id: AlbumId) -> Optional["GPAlbum"]:
#         """will return the album with the specified id if it exists
#         """
#         endpoint = f"https://photoslibrary.googleapis.com/v1/albums/{album_id}"
#         response = gp.request(RequestType.GET, endpoint,
#                               use_json_headers=False)
#         if response.status_code == 200:
#             return GPAlbum.from_dict(gp, response.json())
#         return None

#     @staticmethod
#     def from_name(gp: "gp_wrapper.gp.GooglePhotos", album_name: str, create_on_missing: bool = False)\
#             -> Generator["GPAlbum", None, None]:
#         'will return all albums with the specified name'
#         has_yielded: bool = False
#         for album in GPAlbum.all_albums(gp):
#             if album.title == album_name:
#                 has_yielded = True
#                 yield album

#         if create_on_missing:
#             if not has_yielded:
#                 yield GPAlbum.create(gp, album_name)

#         return

#     def add_description(self, description_parts: Iterable[str],
#                         relative_position: PositionType = PositionType.FIRST_IN_ALBUM,
#                         optional_additional_data: Optional[dict] = None) \
#             -> Iterable[tuple[Optional[Response], Optional[CoreEnrichmentItem]]]:
#         """a facade function that uses 'add_enrichment' to simplify adding a description

#         Args:
#             description (str): description to add
#             relative_position (ALbumPosition, optional): where to add the description.
#                 Defaults to ALbumPosition.FIRST_IN_ALBUM.

#         Returns:
#             EnrichmentItem: the resulting item
#         """
#         HARD_LIMIT: int = 1000
#         # copy the items if it is a generator
#         parts = list(description_parts)
#         for part in parts:
#             if len(part) > HARD_LIMIT:
#                 raise ValueError(
#                     f"the description parts should be less than {HARD_LIMIT} characters"
#                     "long because of a hard limit google employs")

#         chunks: list[str] = []
#         tmp_chunk = ""
#         for text in parts:
#             if len(tmp_chunk) + len(text) >= 1000:
#                 chunks.append(tmp_chunk)
#                 tmp_chunk = ""
#             tmp_chunk += text

#         if len(tmp_chunk) > 0:
#             chunks.append(tmp_chunk)

#         items = []
#         for part in chunks[::-1]:
#             items.append(self.addEnrichment(
#                 EnrichmentType.TEXT_ENRICHMENT,
#                 {"text": part},
#                 relative_position,
#                 album_position_data=optional_additional_data
#             ))
#         return items

#     def get_media(self) -> Iterable[GPMediaItem]:
#         """gets all media in album

#         Returns:
#             Iterable[GooglePhotosMediaItem]: all media of the album

#         Yields:
#             Iterator[Iterable[GooglePhotosMediaItem]]: _description_
#         """
#         endpoint = "https://photoslibrary.googleapis.com/v1/mediaItems:search"
#         data = {
#             "albumId": self.id
#         }
#         response = self.gp.request(
#             RequestType.POST, endpoint, json=data)
#         if not response.status_code == 200:
#             return []
#         j = response.json()
#         if "mediaItems" not in j:
#             return []
#         for dct in j["mediaItems"]:
#             yield GPMediaItem.from_dict(self.gp, dct)

#     @staticmethod
#     def exists(gp: "gp_wrapper.gp.GooglePhotos", /, name: Optional[str] = None, id: Optional[str] = None) -> Optional["GPAlbum"]:
#         for album in GPAlbum.all_albums(gp):
#             if name:
#                 if album.title == name:
#                     return album
#             if id:
#                 if album.id == id:
#                     return album

#         return None


# __all__ = [
#     "GPAlbum",
#     "PositionType",
#     "EnrichmentType"
# ]
