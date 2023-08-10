import time
import enum
import functools
from threading import Lock
import threading
from queue import Queue
from typing import Optional, Union, Callable, TypeVar, Generator, Iterable, Any
from typing_extensions import ParamSpec
from danielutils import info, MinHeap
T = TypeVar("T")
P = ParamSpec("P")
Milliseconds = float
Seconds = float


def declare(obj: Union[Callable[P, T], Optional[str]] = None):
    """will print a string when entering a function

    Args:
        obj (Union[Callable[P, T], Optional[str]], optional): the string to use or None to use default string. Defaults to None.
    """
    msg = obj

    def deco(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if msg is None:
                info(f"\t{func.__name__}")
            else:
                info(msg)
            return func(*args, **kwargs)
        return wrapper
    if callable(obj):
        func = obj
        msg = None
        del obj
        return deco(func)
    del obj
    return deco


def split_iterable(iterable: Iterable[T], batch_size: int) -> Generator[list[T], None, None]:
    """will yield sub-iterables each the size of 'batch_size'

    Args:
        iterable (Iterable[T]): the iterable to split
        batch_size (int): the size of each sub-iterable

    Yields:
        Generator[list[T], None, None]: resulting value
    """
    batch: list[T] = []
    for i, item in enumerate(iterable):
        if i % batch_size == 0:
            if len(batch) > 0:
                yield batch
            batch = []
        batch.append(item)
    yield batch


def json_default(obj: Any) -> dict:
    """a default handler when using json over a non-json-serializable object

    Args:
        obj (Any): non-json-serializable object

    Returns:
        dict: result dict representing said object
    """
    if hasattr(obj, "__json__"):
        return getattr(obj, "__json__")()
    return {obj.__class__.__name__: id(obj)}


def slowdown(interval: Seconds):
    """will slow down function calls to a minimum of specified call over time span

    Args:
        minimal_interval_duration (float): duration to space out calls
    """
    if not isinstance(interval, int | float):
        raise ValueError("minimal_interval_duration must be a number")

    def deco(func: Callable[P, T]) -> Callable[P, T]:
        # q: Queue = Queue()
        index = 0
        # lock = Lock()
        # prev_duration: float = 0
        prev_start: float = -float("inf")
        # heap = MinHeap()

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            nonlocal index, prev_start
            # =============== THREAD SAFETY =============
            # with lock:
            #     current_index = index
            #     index += 1
            #     heap.push(current_index)
            # # maybe need to min(x,x-1)
            # # tasks_before_me = heap.peek()-current_index
            # # time.sleep(tasks_before_me*minimal_interval_duration)

            start = time.time()
            time_passed: Milliseconds = (start-prev_start)/1000
            time_to_wait: Seconds = interval-time_passed
            if time_to_wait > 0:
                time.sleep(time_to_wait)
            res = func(*args, **kwargs)
            prev_start = start
            return res
        return wrapper
    return deco
# def singleton(func: Callable[P, T]):
#     has_been_called_already: bool = False
#     res: T

#     @functools.wraps(func)
#     def wrapper(*args, **kwargs) -> T:
#         nonlocal res, has_been_called_already
#         if not has_been_called_already:
#             res = func(*args, **kwargs)
#             has_been_called_already = True
#         return res
#     return wrapper


class RequestType(enum.Enum):
    GET = "get"
    POST = "post"
    PATCH = "patch"


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


class MaskTypes(enum.Enum):
    """
    available mask values to update for a media item
    see https://developers.google.com/photos/library/reference/rest/v1/mediaItems/patch#query-parameters
    """
    DESCRIPTION = "description"


MediaItemID = str
UploadToken = str
Url = str
AlbumId = str
Path = str
NextPageToken = str
