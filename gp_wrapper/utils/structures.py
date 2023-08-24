import inspect
from enum import Enum
from datetime import datetime
from typing import Optional, IO, cast
from types import FrameType
from abc import ABC, abstractmethod
import gp_wrapper
from .helpers import get_python_version, memo
if get_python_version() < (3, 9):
    from typing import List as t_list  # pylint:disable=ungrouped-imports
else:
    from builtins import list as t_list  # type:ignore
Milliseconds = float
Seconds = float
MediaItemID = str
UploadToken = str
Url = str
AlbumId = str
Path = str
NextPageToken = str
Value = str


# class OnlyPrivateFieldsMeta(type):
#     """will modify a class's __setattr__ so that it's attributes will be
#     private and cannot be changed from outside using "dot notation"

#     An 'AttributeError' will be raised if an attribute will be set not using a class function.
#     """
#     @staticmethod
#     def _get_function_names(cls: type) -> t_set[str]:
#         res = set()
#         for kls in cls.mro():
#             if kls is object:
#                 continue
#             res.update(list(kls.__dict__))
#         return res

#     @staticmethod
#     def _get_prev_frame(frame: Optional[FrameType]) -> Optional[FrameType]:
#         """Get the previous frame (caller's frame) in the call stack.

#         This function retrieves the frame that called the current frame in the Python call stack.

#         Args:
#             frame (Optional[FrameType]): The current frame for which to find the previous frame.

#         Returns:
#             Optional[FrameType]: The previous frame in the call stack, or None if it is not available.

#         Note:
#             If the input frame is None or not of type FrameType, the function returns None.
#         """
#         if frame is None:
#             return None
#         if not isinstance(frame, FrameType):
#             return None
#         frame = cast(FrameType, frame)
#         return frame.f_back

#     @staticmethod
#     def _get_caller_name(steps_back: int = 0) -> Optional[str]:
#         """returns the name caller of the function

#         Returns:
#             str: name of caller

#         USING THIS FUNCTION WHILE DEBUGGING WILL ADD ADDITIONAL FRAMES TO THE TRACEBACK
#         """
#         if not isinstance(steps_back, int):
#             raise TypeError("steps_back must be an int")
#         if steps_back < 0:
#             raise ValueError("steps_back must be a non-negative integer")
#         frame = OnlyPrivateFieldsMeta._get_prev_frame(
#             OnlyPrivateFieldsMeta._get_prev_frame(inspect.currentframe()))
#         if frame is None:
#             return None
#         frame = cast(FrameType, frame)
#         while steps_back > 0:
#             frame = OnlyPrivateFieldsMeta._get_prev_frame(frame)
#             if frame is None:
#                 return None
#             frame = cast(FrameType, frame)
#             steps_back -= 1
#         return frame.f_code.co_name

#     def __new__(mcs, name: str, bases: t_tuple, namespace: dict):
#         def __setattr__(self, name, value):
#             caller = OnlyPrivateFieldsMeta._get_caller_name()
#             if caller in OnlyPrivateFieldsMeta._get_function_names(self.__class__):
#                 return object.__setattr__(self, name, value)
#             raise AttributeError(
#                 f"Attribute '{name}' of '{self.__class__.__name__}' is private and cannot be changed from outside")
#         namespace["__setattr__"] = __setattr__
#         return type(name, bases, namespace)

class OnlyPrivate:
    """will override __setattr__ to make instance's attributes private 
    and so that they can be change only from inside functions
    """
    @classmethod
    @memo
    def __get_function_names(cls, kls: type) -> set:
        res = set()
        mro = kls.mro()
        reversed_last_index = mro[::-1].index(cls)
        last_index = len(mro)-reversed_last_index-1
        for kls_ in mro[:last_index]:
            if kls_ is cls:
                continue
            res.update(list(kls_.__dict__))
        return res

    @staticmethod
    def __get_prev_frame(frame: Optional[FrameType]) -> Optional[FrameType]:
        """Get the previous frame (caller's frame) in the call stack.

        This function retrieves the frame that called the current frame in the Python call stack.

        Args:
            frame (Optional[FrameType]): The current frame for which to find the previous frame.

        Returns:
            Optional[FrameType]: The previous frame in the call stack, or None if it is not available.

        Note:
            If the input frame is None or not of type FrameType, the function returns None.
        """
        if frame is None:
            return None
        if not isinstance(frame, FrameType):
            return None
        frame = cast(FrameType, frame)
        return frame.f_back

    @staticmethod
    def __get_caller_name(steps_back: int = 0) -> Optional[str]:
        """returns the name caller of the function

        Returns:
            str: name of caller

        USING THIS FUNCTION WHILE DEBUGGING WILL ADD ADDITIONAL FRAMES TO THE TRACEBACK
        """
        if not isinstance(steps_back, int):
            raise TypeError("steps_back must be an int")
        if steps_back < 0:
            raise ValueError("steps_back must be a non-negative integer")
        frame = OnlyPrivate.__get_prev_frame(
            OnlyPrivate.__get_prev_frame(inspect.currentframe()))
        if frame is None:
            return None
        frame = cast(FrameType, frame)
        while steps_back > 0:
            frame = OnlyPrivate.__get_prev_frame(frame)
            if frame is None:
                return None
            frame = cast(FrameType, frame)
            steps_back -= 1
        return frame.f_code.co_name

    def __setattr__(self, name, value):
        caller = OnlyPrivate.__get_caller_name()
        if caller in OnlyPrivate.__get_function_names(self.__class__):
            return object.__setattr__(self, name, value)
        raise AttributeError(
            f"Attribute '{name}' of '{self.__class__.__name__}' is private and cannot be changed from outside")


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
            for cls in self.__class__.mro():
                potential_prefix = f"_{cls.__name__}__"
                if k.startswith(potential_prefix):
                    k = k[len(potential_prefix):]
                    break
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
    @staticmethod
    @abstractmethod
    def from_dict(dct: dict):
        """creates an object from relevant dict
        """

    def to_dict(self) -> dict:
        """returns a dictionary representation of object"""
        res = {}
        for k, v in self.__dict__.items():
            potential_prefix = f"_{self.__class__.__name__}__"
            if k.startswith(potential_prefix):
                k = k[len(potential_prefix):]
            if isinstance(v, Dictable):
                res[k] = v.to_dict()
            else:
                res[k] = v
        return res


class SimpleMediaItem(Dictable, Printable):
    """A simple media item to be created in Google Photos via an upload token.

    Args:
        uploadToken (str): Token identifying the media bytes that have been uploaded to Google.
        fileName (Optional[str]): File name with extension of the media item. 
            This is shown to the user in Google Photos. 
            The file name specified during the byte upload process is ignored if this field is set. 
            The file name, including the file extension, shouldn't be more than 255 characters. 
            This is an optional field.

    Raises:
        ValueError: fileName's length must be less than 256 characters long
    """
    # see https://developers.google.com/photos/library/reference/rest/v1/mediaItems/batchCreate#SimpleMediaItem

    @staticmethod
    def from_dict(dct: dict):
        return SimpleMediaItem(
            uploadToken=dct["uploadToken"],
            fileName=dct["fileName"] if "fileName" in dct else None
        )

    def __init__(self, uploadToken: str, fileName: Optional[str] = None) -> None:
        if fileName:
            if len(fileName) > 255:
                raise ValueError(
                    "'fileName' must not be more than 255 characters or the request will fail")
        self.__uploadToken = uploadToken
        self.__fileName = fileName

    @property
    def fileName(self):
        """File name with extension of the media item. 
        This is shown to the user in Google Photos. 
        The file name specified during the byte upload process is ignored if this field is set. 
        The file name, including the file extension, shouldn't be more than 255 characters. 
        This is an optional field.
        """
        return self.__fileName

    @property
    def uploadToken(self):
        """Token identifying the media bytes that have been uploaded to Google.
        """
        return self.__uploadToken


class NewMediaItem(Dictable, Printable):
    """New media item that's created in a user's Google Photos account.

    Args:
        description (str): Description of the media item. 
        This is shown to the user in the item's info section in the Google Photos app. 
        Must be shorter than 1000 characters. Only include text written by users. 
        Descriptions should add context and help users understand media. 
        Do not include any auto-generated strings such as filenames, tags, and other metadata.
        simpleMediaItem (SimpleMediaItem): A new media item that has been uploaded via the included uploadToken.

    Raises:
        ValueError: if description is more than 1000 characters long

    """
    @staticmethod
    def from_dict(dct: dict):
        return NewMediaItem(
            description=dct["description"],
            simpleMediaItem=SimpleMediaItem.from_dict(dct["simpleMediaItem"])
        )

    def __init__(self, description: str, simpleMediaItem: SimpleMediaItem) -> None:
        """_summary_

        Args:
            description (str): Description of the media item. 
            This is shown to the user in the item's info section in the Google Photos app. 
            Must be shorter than 1000 characters. Only include text written by users. 
            Descriptions should add context and help users understand media. 
            Do not include any auto-generated strings such as filenames, tags, and other metadata.
            simpleMediaItem (SimpleMediaItem): A new media item that has been uploaded via the included uploadToken.

        Raises:
            ValueError: if description is more than 1000 characters long
        """

        if description:
            if len(description) > 1000:
                raise ValueError(
                    "\"description\"'s length should be shorter than 1000 characters long")
        self.__description = description
        self.__simpleMediaItem = simpleMediaItem

    @property
    def description(self):
        return self.__description

    @property
    def simpleMediaItem(self):
        return self.__simpleMediaItem


class AlbumPosition(Dictable, Printable):
    """Specifies a position in an album.

        Args:
            position (PositionType, optional): Type of position, for a media or enrichment item. 
                Defaults to PositionType.FIRST_IN_ALBUM.
            relativeMediaItemId (Optional[str], optional): The media item to which the position is relative to. 
                Only used when position type is AFTER_MEDIA_ITEM. Defaults to None.
            relativeEnrichmentItemId (Optional[str], optional): 
                The enrichment item to which the position is relative to. 
                Only used when position type is AFTER_ENRICHMENT_ITEM. Defaults to None.

        Raises:
            ValueError: if both 'relativeMediaItemId' and 'relativeEnrichmentItemId' is used
        """
    @staticmethod
    def from_dict(dct: dict):
        return AlbumPosition(
            position=dct["position"],
            relativeMediaItemId=dct["relativeMediaItemId"] if "relativeMediaItemId" in dct else None,
            relativeEnrichmentItemId=dct["relativeEnrichmentItemId"] if "relativeEnrichmentItemId" in dct else None
        )

    def __init__(self, position: PositionType = PositionType.FIRST_IN_ALBUM, *,
                 relativeMediaItemId: Optional[str] = None,
                 relativeEnrichmentItemId: Optional[str] = None) -> None:

        self.__position = position
        self.__relativeMediaItemId = None
        self.__relativeEnrichmentItemId = None
        if self.position in {PositionType.AFTER_MEDIA_ITEM, PositionType.AFTER_ENRICHMENT_ITEM}:
            if (not relativeMediaItemId and not relativeEnrichmentItemId) \
                    or (relativeEnrichmentItemId and relativeEnrichmentItemId):
                raise ValueError(
                    "Must supply exactly one between 'relativeMediaItemId' and 'relativeEnrichmentItemId'")
            if relativeMediaItemId:
                self.__relativeMediaItemId = relativeMediaItemId
            else:
                self.__relativeEnrichmentItemId = relativeEnrichmentItemId

    @property
    def position(self):
        """Type of position, for a media or enrichment item.
        """
        return self.__position

    @property
    def relativeMediaItemId(self):
        """The media item to which the position is relative to. 
        Only used when position type is AFTER_MEDIA_ITEM.
        """
        return self.__relativeMediaItemId

    @property
    def relativeEnrichmentItemId(self):
        """The enrichment item to which the position is relative to. 
        Only used when position type is AFTER_ENRICHMENT_ITEM.
        """
        return self.__relativeEnrichmentItemId


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


class Status(Dictable, Printable):
    """
    see https://developers.google.com/photos/library/reference/rest/v1/Status
    """
    @staticmethod
    def from_dict(dct: dict):
        return Status(
            message=dct["message"],
            code=dct["code"] if "code" in dct else None,
            details=dct["details"] if "details" in dct else None
        )

    def __init__(self, message: str, code: Optional[StatusCode] = None, details: Optional[t_list[dict]] = None) -> None:
        self.__message = message
        self.__code = code
        self.__details = details

    @property
    def message(self):
        return self.__message

    @property
    def code(self):
        return self.__code

    @property
    def details(self):
        return self.__details


class MediaItemResult(Dictable, Printable):
    """Result of creating a new media item.

    Args:
        mediaItem (Optional[&quot;gp_wrapper.MediaItem&quot;], optional): 
            Media item created with the upload token. 
            It's populated if no errors occurred and the media item was created successfully. 
            Defaults to None.
        status (Optional[Status], optional): 
            If an error occurred during the creation of this media item, this field is populated with
            information related to the error. For details regarding this field, see Status. 
            Defaults to None.
        uploadToken (Optional[str], optional): 
            The upload token used to create this new (simple) media item.
            Only populated if the media item is simple and required a single upload token.
            Defaults to None.
    """
    @staticmethod
    def from_dict(dct: dict):
        return MediaItemResult(
            mediaItem=gp_wrapper.MediaItem.from_dict(
                gp=dct["gp"],
                dct=dct["mediaItem"]
            ) if "mediaItem" in dct else None,
            status=Status.from_dict(dct["status"]) if "status" in dct else None,  # noqa
            uploadToken=dct["uploadToken"] if "uploadToken" in dct else None,
        )

    def __init__(self, mediaItem: Optional["gp_wrapper.MediaItem"] = None, status: Optional[Status] = None,
                 uploadToken: Optional[str] = None) -> None:  # type:ignore

        self.__uploadToken = uploadToken
        self.__status = status
        self.__mediaItem = mediaItem

    @property
    def uploadToken(self):
        """The upload token used to create this new (simple) media item. 
        Only populated if the media item is simple and required a single upload token."""
        return self.__uploadToken

    @property
    def status(self):
        """If an error occurred during the creation of this media item, 
        this field is populated with information related to the error.
        For details regarding this field, see Status."""
        return self.__status

    @property
    def mediaItem(self):
        """Media item created with the upload token. 
        It's populated if no errors occurred and the media item was created successfully.
        """
        return self.__mediaItem


class MediaMetadata(Dictable, Printable):
    """Metadata for a media item.

    Args:
        creationTime (str): Time when the media item was first created (not when it was uploaded to Google Photos).
            A timestamp in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to nine fractional digits.
            Examples: "2014-10-02T15:01:23Z" and "2014-10-02T15:01:23.045123456Z".
        width (Optional[str], optional): Original width (in pixels) of the media item. Defaults to None.
        height (Optional[str], optional): Original height (in pixels) of the media item. Defaults to None.
        photo (Optional[dict], optional): Metadata for a photo media type. Defaults to None.
        video (Optional[dict], optional): Metadata for a video media type. Defaults to None.
    """
    @staticmethod
    def from_dict(dct: dict) -> "MediaMetadata":
        return MediaMetadata(
            creationTime=dct["creationTime"],
            width=dct["width"] if "width" in dct else None,
            height=dct["height"] if "height" in dct else None,
            photo=dct["photo"] if "photo" in dct else None,
            video=dct["video"] if "video" in dct else None,
        )

    def __init__(
        self,
        creationTime: str,
        width: Optional[str] = None,
        height: Optional[str] = None,
        photo: Optional[dict] = None,
        video: Optional[dict] = None
    ) -> None:
        FORMAT = "%Y-%m-%dT%H:%M:%SZ"
        self.__creationTime: datetime = datetime.strptime(creationTime, FORMAT)
        self.__width: Optional[int] = int(width) if width else None
        self.__height: Optional[int] = int(height) if height else None
        self.__photo = photo
        self.__video = video

    @property
    def creationTime(self):
        return self.__creationTime

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def photo(self):
        return self.__photo

    @property
    def video(self):
        return self.__video


class ContributorInfo(Dictable, Printable):
    """Information about the user who added the media item.
    Note that this information is included only if the media item is within a shared album created by
    your app and you have the sharing scope.

    Args:
        profilePictureBaseUrl (str): URL to the profile picture of the contributor.
        displayName (str): Display name of the contributor.
    """
    @staticmethod
    def from_dict(dct: dict) -> "ContributorInfo":
        return ContributorInfo(
            profilePictureBaseUrl=dct["profilePictureBaseUrl"],
            displayName=dct["displayName"]
        )

    def __init__(self, profilePictureBaseUrl: str, displayName: str) -> None:

        self.__profilePictureBaseUrl = profilePictureBaseUrl
        self.__displayName = displayName

    @property
    def profilePictureBaseUrl(self) -> str:
        return self.__profilePictureBaseUrl

    @property
    def displayName(self) -> str:
        return self.__displayName


# class MultiPartEncoderWithProgress(MultipartEncoder):
#     def __init__(self, tqdm_options: dict, fields, boundary=None, encoding='utf-8'):
#         super().__init__(fields, boundary, encoding)
#         self.tqdm_options = tqdm_options

#     def _load(self, amount):
#         if not hasattr(self, "tqdm"):
#             setattr(self, "tqdm", tqdm(**self.tqdm_options))
#         MultipartEncoder._load(self, amount)
#         self.tqdm.update(amount/self.len * 100)  # pylint: disable=no-member


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
