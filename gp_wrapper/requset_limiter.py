from typing import Callable
from queue import Queue
import time
JobId = int


def slowdown(minimal_interval_duration: float):
    def deco(func):
        prev_duration: float = 0
        prev_start_time: float = -float("inf")

        def wrapper(*args, **kwargs):
            start = time.time()
            if start-prev_start_time > minimal_interval_duration:
                time.sleep(min(start-prev_start_time,
                           minimal_interval_duration))
            res = func(*args, **kwargs)
            end = time.time()
            duration = end-start
            return res
        return wrapper
    return deco


class RequestLimiter:
    def __init__(self, google_limit_quota: int) -> None:
        self.quota = google_limit_quota
        self.q: Queue = Queue()
        self.count = 0

    def submit(self, func, args, kwargs) -> JobId:
        self.q.put((func, args, kwargs))
        self.count += 1
        return self.count-1

    def run(self, blocking: bool = True):
        pass

    @slowdown(2)
    def _execute_job(self):
        func, args, kwargs = self.q.get()
        return func(*args, **kwargs)
