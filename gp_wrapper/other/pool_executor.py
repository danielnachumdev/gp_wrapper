from threading import Thread
from queue import Queue
from typing import Callable
from danielutils import threadify, decorate_conditionally


class ThreadPoolExecutor:
    def __init__(self, num_workers: int, entry_point: Callable) -> None:
        self.num_workers = num_workers
        self.entry_point = entry_point
        self.currently_running: int = 0
        self.q: Queue = Queue()
        self.workers: set[Thread] = set()

    def submit(self, args: tuple = tuple(), kwargs: dict = dict()):
        self.q.put((args, kwargs))

    def run(self, blocking: bool = True) -> None:
        # initialize
        for _ in range(self.num_workers):
            if not self.q.empty():
                args, kwargs = self.q.get()
                w = Thread(target=self.entry_point, args=args, kwargs=kwargs)
                self.workers.add(w)
                w.start()

        @decorate_conditionally(threadify, not blocking)
        def scaling_logic():
            while self.q.unfinished_tasks > 0:
                to_remove = set()
                for w in self.workers:
                    if not w.is_alive():
                        to_remove.add(w)

                for _ in range(len(to_remove)):
                    self.q.task_done()
                self.workers.difference_update(to_remove)

                maximum_allowed = min(
                    self.q.unfinished_tasks, self.num_workers)
                if len(self.workers) < maximum_allowed:
                    for _ in range(maximum_allowed-len(self.workers)):
                        args, kwargs = self.q.get()
                        w = Thread(target=self.entry_point,
                                   args=args, kwargs=kwargs)
                        self.workers.add(w)
                        w.start()
        scaling_logic()

    def has_finished(self) -> bool:
        for w in self.workers:
            if w.is_alive():
                return False
        return True
