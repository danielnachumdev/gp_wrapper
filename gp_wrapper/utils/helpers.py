import functools
import time
import platform
from typing import Callable, TypeVar, Generator, Iterable, Any, ForwardRef


def _get_python_version_untyped() -> tuple:
    values = (int(v) for v in platform.python_version().split("."))
    try:
        return tuple(values)  # type:ignore
    except:
        from builtins import tuple
        return tuple(values)  # type:ignore


if _get_python_version_untyped() < (3, 9):
    from typing import Tuple as tuple, List as list
else:
    from builtins import tuple, list  # type:ignore


def get_python_version() -> tuple[int, int, int]:
    """return the version of python that is currently running this code

    Returns:
        tuple[int, int, int]: version
    """
    return _get_python_version_untyped()  # type:ignore


if get_python_version() < (3, 9):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec  # type:ignore
P = ParamSpec("P")
T = TypeVar("T")


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


def json_default(obj: Any) -> str:
    """a default handler when using json over a non-json-serializable object

    Args:
        obj (Any): non-json-serializable object

    Returns:
        dict: result dict representing said object
    """
    if hasattr(obj, "__json__"):
        return getattr(obj, "__json__")()
    if hasattr(obj, "__dict__") and obj.__module__.split(".")[0] == "gp_wrapper":
        # json.dumps(obj.__dict__, indent=4, default=json_default)
        return str(obj)
    return str(id(obj))


def slowdown(interval: ForwardRef("Seconds")):  # type:ignore
    """will slow down function calls to a minimum of specified call over time span

    Args:
        minimal_interval_duration (float): duration to space out calls
    """
    from .structures import Seconds, Milliseconds
    if not isinstance(interval, (int, float)):
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


__all__ = [
    # "declare",
    "split_iterable",
    "json_default",
    "slowdown",
    "get_python_version"
]
