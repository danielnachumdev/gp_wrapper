import math
from threading import Thread, Semaphore
from typing import Generator, Optional, Callable
from queue import Queue
from requests.models import Response

from gp_wrapper.objects.core.gp import CoreGooglePhotos
from gp_wrapper.objects.core.media_item.core_media_item import CoreGPMediaItem
from gp_wrapper.objects.core.media_item.filters import SearchFilter
from gp_wrapper.utils import NextPageToken
from .core import CoreGooglePhotos, CoreGPMediaItem
from ..utils import MediaItemMaskTypes


class GPMediaItem(CoreGPMediaItem):
    @staticmethod
    def _from_core(c: CoreGPMediaItem) -> "GPMediaItem":
        return GPMediaItem(**c.__dict__)

    @staticmethod
    def from_dict(gp: CoreGooglePhotos, dct: dict) -> "GPMediaItem":
        return GPMediaItem._from_core(GPMediaItem._from_dict(gp, dct))

    def set_description(self, description: str) -> Response:
        return self.patch(MediaItemMaskTypes.DESCRIPTION, description)

    @staticmethod
    def search_all(
        gp: CoreGooglePhotos,
        albumId: str | None = None,
        pageSize: int = 25,
        filters: SearchFilter | None = None,
        orderBy: str | None = None,
        tokens_to_use: int = math.inf,  # type:ignore
        pre_fetch: bool = False
    ) -> Generator["GPMediaItem", None, None]:
        """like CoreGPMediaItem.search but automatically converts the objects to the
        higher order class and automatically uses the tokens to get all objects

        Additional Args:
            tokens_to_use (int): how many times to use the token automatically to fetch the next batch.
                Defaults to using all tokens.
            pre_fetch (Boolean): whether to non-blocking-ly fetch ALL available items using the tokens
                Defaults to False.
        """
        q: Queue[GPMediaItem] = Queue()
        sem = Semaphore(0)
        if not (0 < tokens_to_use):
            raise ValueError(
                "'tokens_to_use' should be a positive integer")

        def inner_logic(blocking: bool = True) -> Optional[Generator]:
            nonlocal tokens_to_use
            core_gen, pageToken = CoreGPMediaItem.search(
                gp, albumId, pageSize, None, filters, orderBy)
            tokens_to_use -= 1
            for o in (GPMediaItem._from_core(o) for o in core_gen):
                if blocking:
                    yield o
                else:
                    q.put(o)
                sem.release()
            while pageToken and tokens_to_use > 0:
                core_gen, pageToken = CoreGPMediaItem.search(
                    gp, albumId, pageSize, pageToken, filters, orderBy)
                tokens_to_use -= 1
                for o in (GPMediaItem._from_core(o) for o in core_gen):
                    if blocking:
                        yield o
                    else:
                        q.put(o)
                    sem.release()
        if pre_fetch:
            # TODO fix this part
            raise NotImplementedError("pre_fetch is currently not supported")
            t = Thread(target=inner_logic, args=(False,))
            t.start()
            with sem:
                # re-add value that was used as a barrier
                sem.release()
                while not q.empty():
                    with sem:
                        yield q.get()
        else:
            yield from inner_logic()  # type:ignore


__all__ = [
    "GPMediaItem",
    "MediaItemMaskTypes"
]
