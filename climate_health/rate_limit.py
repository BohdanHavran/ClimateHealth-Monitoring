"""Bounded, process-local fixed-window limits. Not a distributed quota store."""

from collections import OrderedDict
from threading import Lock
from time import monotonic


class WindowLimiter:
    def __init__(self, limit, seconds, capacity=2048, clock=monotonic):
        self.limit, self.seconds, self.capacity = limit, seconds, capacity
        self.clock, self.entries, self.lock = clock, OrderedDict(), Lock()

    def allow(self, key):
        now = self.clock()
        with self.lock:
            start, count = self.entries.pop(key, (now, 0))
            if now - start >= self.seconds:
                start, count = now, 0
            self.entries[key] = (start, count + 1)
            if len(self.entries) > self.capacity:
                self.entries.popitem(last=False)
            return count < self.limit
