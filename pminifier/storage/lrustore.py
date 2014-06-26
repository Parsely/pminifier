import hashlib
import pylru

from pminifier import utils
from pminifier.storage import StorageBase

class LRUStore(StorageBase):
    """LRU implementation that can be a cache."""

    def __init__(self, lru_size):
        self._counter = 0
        self.lru = pylru.lrucache(lru_size)

    def cache_get_id_multi(self, results):
        for string, id_ in results.iteritems():
            self.lru[('s', string)] = id_
            self.lru[('i', id_)] = string

    def cache_get_string_multi(self, results):
        for id_, string in results.iteritems():
            self.lru[('s', string)] = id_
            self.lru[('i', id_)] = string

    def get_id(self, string, create_missing=False):
        return self.get_id_multi(
            [string],
            create_missing=create_missing
        ).get(string)

    def get_id_multi(self, strings, create_missing=False):
        if create_missing:
            raise NotImplementedError("LRU can't be a long-term store.")
        return {s: self.lru[('s', s)] if ('s', s) in self.lru else None
                for s in strings}

    def get_string_multi(self, ids):
        return {i: self.lru[('i', i)] if ('i', i) in self.lru else None
                for i in ids}
