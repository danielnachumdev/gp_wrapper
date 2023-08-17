import json
import math
from enum import Enum
from datetime import datetime
from typing import Optional, IO, Iterable
from abc import ABC, abstractmethod
from tqdm import tqdm  # type:ignore # pylint: disable=import-error
import gp_wrapper
from .helpers import get_python_version
if get_python_version() < (3, 9):
    from typing import List as t_list  # pylint:disable=ungrouped-imports
else:
    from builtins import list as t_list
Milliseconds = float
Seconds = float
MediaItemID = str
UploadToken = str
Url = str
AlbumId = str
Path = str
NextPageToken = str
Value = str


class RequestType(Enum):
    GET = "get"
    POST = "post"
    PATCH = "patch"


class HeaderType(Enum):
    DEFAULT = ""
    JSON = "json"
    OCTET = "octet-stream"


class MimeType(Enum):
    PNG = "image/png"
    JPEG = "image/jpeg"
    MP4 = "video/mp4"
    MOV = "video/quicktime"


class PositionType(Enum):
    """enum to be used with GooglePhotosAlbum.add_enrichment to specify
    the relative location of the enrichment in the album
    """
    POSITION_TYPE_UNSPECIFIED = "POSITION_TYPE_UNSPECIFIED"
    FIRST_IN_ALBUM = "FIRST_IN_ALBUM"
    LAST_IN_ALBUM = "LAST_IN_ALBUM"
    AFTER_MEDIA_ITEM = "AFTER_MEDIA_ITEM"
    AFTER_ENRICHMENT_ITEM = "AFTER_ENRICHMENT_ITEM"


class EnrichmentType(Enum):
    """enum to be used with GooglePhotosAlbum.add_enrichment to specify the type of enrichment
    """
    TEXT_ENRICHMENT = "textEnrichment"
    LOCATION_ENRICHMENT = "locationEnrichment"
    MAP_ENRICHMENT = "mapEnrichment"


class MediaItemMaskTypes(Enum):
    """
    available mask values to update for a media item
    see https://developers.google.com/photos/library/reference/rest/v1/mediaItems/patch#query-parameters
    """
    DESCRIPTION = "description"


class AlbumMaskType(Enum):
    TITLE = "title"
    COVER_PHOTOS_MEDIA_ITEM_ID = "coverPhotoMediaItemId"


class RelativeItemType(Enum):
    relativeMediaItemId = "relativeMediaItemId",
    relativeEnrichmentItemId = "relativeEnrichmentItemId"


class IndentedWriter2:
    """every class that will inherit this class will have the following functions available
        write() with the same arguments a builtin print()
        indent()
        undent()

        also, it is expected in the __init__ function to call super().__init__()
        also, the output_stream must be set whether by the first argument io super().__init__(...)
        or by set_stream() explicitly somewhere else.

        this class will not function properly is the output_stream is not set!

    """

    def __init__(self, indent_value: str = "\t"):
        self.indent_level = 0
        self.indent_value = indent_value
        self.buffer: str = ""

    def to_stream(self, stream: IO[str]) -> None:
        """outputs the buffer to a stream

        Args:
            stream (IO[str]): the stream to output to
        """
        stream.write(self.buffer)

    def add_from(self, s: str) -> None:
        for i, line in enumerate(s.splitlines()):
            if i == 0:
                self.buffer += line+"\n"
            else:
                self.write(line)

    def write(self, *args, sep=" ", end="\n") -> None:
        """writes the supplied arguments to the output_stream

        Args:
            sep (str, optional): the str to use as a separator between arguments. Defaults to " ".
            end (str, optional): the str to use as the final value. Defaults to "\n".

        Raises:
            ValueError: _description_
        """
        self.buffer += str(self.indent_level *
                           self.indent_value + sep.join(args)+end)

    def indent(self) -> None:
        """indents the preceding output with write() by one quantity more
        """
        self.indent_level += 1

    def undent(self) -> None:
        """un-dents the preceding output with write() by one quantity less
            has a minimum value of 0
        """
        self.indent_level = max(0, self.indent_level-1)


class Printable:
    def __str__(self) -> str:
        w = IndentedWriter2(indent_value=" "*4)
        # w.write(f"{self.__class__.__name__} ", end="")
        w.write("{")
        w.indent()
        for k, v in self.__dict__.items():
            w.write(f"\"{k}\": ", end="")
            if isinstance(v, Printable):
                w.add_from(str(v))
                w.buffer = w.buffer[:-1]+",\n"
            else:
                w.buffer += (f"\"{v}\",\n")
        w.buffer = w.buffer[:-2]+"\n"
        w.undent()
        w.write("}")
        return w.buffer


class Dictable(ABC):
    @abstractmethod
    def to_dict(self) -> dict: ...


class SimpleMediaItem(Dictable, Printable):
    # see https://developers.google.com/photos/library/reference/rest/v1/mediaItems/batchCreate#SimpleMediaItem
    def __init__(self, uploadToken: str, fileName: str) -> None:
        if len(fileName) > 255:
            raise ValueError(
                "'fileName' must not be more than 255 characters or the request will fail")
        self.uploadToken = uploadToken
        self.fileName = fileName

    def to_dict(self) -> dict:
        return self.__dict__


class NewMediaItem(Dictable, Printable):
    @staticmethod
    def from_dict(token: UploadToken, description: str = "", filename: str = "") -> "NewMediaItem":
        return NewMediaItem(
            description,
            SimpleMediaItem(
                token,
                filename
            )
        )

    def __init__(self, description: str, simpleMediaItem: SimpleMediaItem) -> None:
        self.description = description
        self.simpleMediaItem = simpleMediaItem

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "simpleMediaItem": self.simpleMediaItem.to_dict()
        }


class AlbumPosition(Dictable, Printable):
    def __init__(self, position: PositionType = PositionType.FIRST_IN_ALBUM, /,
                 relativeMediaItemId: Optional[str] = None,
                 relativeEnrichmentItemId: Optional[str] = None) -> None:
        self.position = position
        if position in {PositionType.AFTER_MEDIA_ITEM, PositionType.AFTER_ENRICHMENT_ITEM}:
            if (not relativeMediaItemId and not relativeEnrichmentItemId) \
                    or (relativeEnrichmentItemId and relativeEnrichmentItemId):
                raise ValueError(
                    "Must supply exactly one between 'relativeMediaItemId' and 'relativeEnrichmentItemId'")
            if relativeMediaItemId:
                self.relativeMediaItemId = relativeMediaItemId
            else:
                self.relativeEnrichmentItemId = relativeEnrichmentItemId

    def to_dict(self) -> dict:
        dct: dict = self.__dict__.copy()
        dct["position"] = self.position.value
        return dct


class StatusCode(Enum):
    """
    see https://developers.google.com/photos/library/reference/rest/v1/Status
    and https://github.com/googleapis/googleapis/blob/master/google/rpc/code.proto
    """
    OK = 0
    CANCELLED = 1
    UNKNOWN = 2
    INVALID_ARGUMENT = 3
    DEADLINE_EXCEEDED = 4
    NOT_FOUND = 5
    ALREADY_EXISTS = 6
    PERMISSION_DENIED = 7
    UNAUTHENTICATED = 16
    RESOURCE_EXHAUSTED = 8
    FAILED_PRECONDITION = 9
    ABORTED = 10
    OUT_OF_RANGE = 11
    UNIMPLEMENTED = 12
    INTERNAL = 13
    UNAVAILABLE = 14
    DATA_LOSS = 15


class Status(Printable):
    """
    see https://developers.google.com/photos/library/reference/rest/v1/Status
    """
    @staticmethod
    def from_dict(dct) -> "Status":
        return Status(
            message=dct["message"],
            code=dct["code"] if "code" in dct else None,
            details=dct["details"] if "details" in dct else None
        )

    def __init__(self, message: str, code: Optional[StatusCode] = None, details: Optional[t_list[dict]] = None) -> None:
        self.message = message
        self.code = code
        self.details = details


class MediaItemResult(Printable):
    @staticmethod
    def from_dict(gp: "gp_wrapper.GooglePhotos", dct: dict) -> "MediaItemResult":
        return MediaItemResult(
            mediaItem=gp_wrapper.MediaItem.from_dict(
                gp, dct["mediaItem"]) if "mediaItem" in dct else None,
            status=Status.from_dict(
                dct["status"]) if "status" in dct else None,
            uploadToken=dct["uploadToken"] if "uploadToken" in dct else None,
        )
    def __init__(self, mediaItem: Optional["gp_wrapper.MediaItem"] = None, status: Optional[Status] = None,
                 uploadToken: Optional[str] = None) -> None:  # type:ignore
        self.uploadToken = uploadToken
        self.status = status
        self.mediaItem = mediaItem


class MediaMetadata(Dictable, Printable):
    @staticmethod
    def from_dict(dct: dict) -> "MediaMetadata":
        return MediaMetadata(**dct)

    def __init__(self, creationTime: str, width: Optional[str] = None, height: Optional[str] = None, photo: Optional[dict] = None) -> None:
        FORMAT = "%Y-%m-%dT%H:%M:%SZ"
        self.creationTime: datetime = datetime.strptime(creationTime, FORMAT)
        self.width: Optional[int] = int(width) if width else None
        self.height: Optional[int] = int(height) if height else None
        self.photo = photo

    def to_dict(self) -> dict:
        return json.loads(json.dumps(self.__dict__))


# class MultiPartEncoderWithProgress(MultipartEncoder):
#     def __init__(self, tqdm_options: dict, fields, boundary=None, encoding='utf-8'):
#         super().__init__(fields, boundary, encoding)
#         self.tqdm_options = tqdm_options

#     def _load(self, amount):
#         if not hasattr(self, "tqdm"):
#             setattr(self, "tqdm", tqdm(**self.tqdm_options))
#         MultipartEncoder._load(self, amount)
#         self.tqdm.update(amount/self.len * 100)  # pylint: disable=no-member


class ProgressBarInjector:
    """allows seeing an indication of the progress of the request using tqdm
    """

    def __init__(self, data: bytes, tqdm: tqdm, chunk_size: int = 8192) -> None:
        self.data = data
        self._len = len(self.data)
        self.tqdm = tqdm
        self.chunk_size = chunk_size

    def __len__(self) -> int:
        return self._len

    def __iter__(self) -> Iterable[bytes]:
        num_of_chunks = math.ceil(len(self)/self.chunk_size)
        chunks = (self.data[i:i + self.chunk_size]
                  for i in range(0, len(self), self.chunk_size))
        KB = 1024
        MB = 1024*KB
        GB = 1024*MB

        if len(self)/GB > 1:
            total = len(self)/GB
            unit = "GB"
        elif len(self)/MB > 1:
            total = len(self)/MB
            unit = "MB"
        else:
            total = len(self)/KB
            unit = "KB"

        update_amount = total/num_of_chunks
        self.tqdm.unit = unit
        self.tqdm.total = total
        for chunk in chunks:
            yield chunk
            self.tqdm.update(update_amount)
        self.tqdm.reset()


SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary',
    "https://www.googleapis.com/auth/photoslibrary.appendonly",
    "https://www.googleapis.com/auth/photoslibrary.sharing",
    "https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata"
]
EMPTY_PROMPT_MESSAGE = ""
DEFAULT_NUM_WORKERS: int = 2
ALBUMS_ENDPOINT = "https://photoslibrary.googleapis.com/v1/albums"
UPLOAD_MEDIA_ITEM_ENDPOINT = "https://photoslibrary.googleapis.com/v1/uploads"
MEDIA_ITEMS_CREATE_ENDPOINT = "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"
