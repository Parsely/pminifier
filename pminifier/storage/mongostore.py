import logging
import pymongo

from functools import wraps
from pymongo.errors import AutoReconnect

from pminifier import utils
from pminifier.storage import StorageBase

def retry(f):
    """Retry an operation 100 times, waiting 1s between retries"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        fails = 0
        try:
            return f(*args, **kwargs)
        except AutoReconnect:
            fails += 1
            if fails == 1:
                log.warning('Connection to PRIMARY interrupted. Reconnecting')
            if fails >= 100:
                raise # no good. too many fails
            time.sleep(1.0)
    return wrapper

class MongoStore(StorageBase):
    """Long-term storage implementation using MongoDB"""

    def __init__(self, conn_info, dbname):
        """Initialize mongo and ensure indexes.

        :param dbname: The name of the database to use.
        :param conn_info: A dict containing all parameters going to the
            pymongo constructor. To use a repliaset connection, be sure
            `replicaSet` is in the dict.
        """
        if 'replicaSet' in conn_info:
            conn = pymongo.MongoReplicaSetClient(**conn_info)
        else:
            conn = pymongo.MongoClient(**conn_info)
        self.db = conn[dbname]
        self.db.minifiedStrings.ensure_index(
            [('string', 1)], unique=True, background=False
        )

    @retry
    def _next_id(self):
        """Get the next id from the minifierMeta collection."""
        counter = self.db.minifierMeta.find_and_modify(
            query={'_id': 'next_id'},
            update={'$inc': {'value': 1}},
            upsert=True,
            new=True
        )
        return utils.int_to_base62(counter['value']-1) # -1 so we 0-index

    def cache_get_id_multi(self, results):
        raise NotImplementedError("Mongo is not a cache.")

    def cache_get_string_multi(self, results):
        raise NotImplementedError("Mongo is not a cache.")

    @retry
    def get_id_multi(self, strings, create_missing=True):
        if not strings:
            return None
        entries = self.db.minifiedStrings.find({'string': {'$in': strings}},
                                               fields=['_id', 'string'])
        output = {e['string']: e['_id'] for e in entries}

        missing = set(strings) - set(output.iterkeys())
        if not missing:
            return output
        # Create new entry for keys not found
        if create_missing:
            for string in missing:
                id_ = self._next_id()
                # FIXME: Catch unique index violations
                self.db.minifiedStrings.insert({'_id': id_, 'string': string})
                output[string] = id_
        else:
            output.update((s, None) for s in strings if s not in output)
        return output

    @retry
    def get_string_multi(self, ids):
        entries = self.db.minifiedStrings.find({'_id': {'$in': ids}},
                                               fields=['string'])
        output = {e['_id']: e['string'] for e in entries}
        output.update((id_, None) for id_ in ids if id_ not in output)
        return output
