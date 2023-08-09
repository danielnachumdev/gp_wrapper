import functools
from typing import Optional, Union, Callable, TypeVar, Generator, Iterable, Any
from typing_extensions import ParamSpec
from danielutils import info
T = TypeVar("T")
P = ParamSpec("P")


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


MediaItemID = str
UploadToken = str
Url = str
AlbumId = str
Path = str
