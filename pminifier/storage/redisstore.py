import hashlib
import redis

from itertools import izip

from pminifier import utils
from pminifier.storage import StorageBase

class RedisStore(StorageBase):
    """Redis implementation that can be a cache or long-term store."""

    def __init__(self, conn_info):
        self.redis = redis.StrictRedis(**conn_info)

    def _get_ids(self, num_to_create):
        """Get the next ``num_to_create`` ids.

        :returns: an xrange object iterating over the ids to use
        """
        end = self.redis.incrby('pminifier:next_id', num_to_create)
        return xrange(end-num_to_create, end)

    def cache_get_id_multi(self, results):
        pass

    def cache_get_string_multi(self, results):
        pass

    def get_id_multi(self, strings, create_missing=True):
        if not strings:
            return None
        entries = self.redis.mget(
            'pm:s:{}'.format(hashlib.sha1(s).hexdigest()) for s in strings
        )
        output = dict(izip(strings, entries))
        if create_missing and any(v is None for v in output.itervalues()):
            # Create new IDs in redis for these
            missing = [k for k,v in output.iteritems() if v is None]
            new_ids = {m: utils.int_to_base62(i)
                       for m, i in izip(missing, self._get_ids(len(missing)))}
            output.update(new_ids)
            # Save it once by the string hash and once by the actual id
            self.redis.mset({
                'pm:s:{}'.format(hashlib.sha1(s).hexdigest()): i
                for s, i in new_ids.iteritems()
            })
            self.redis.mset({
                'pm:i:{}'.format(i): s
                for s, i in new_ids.iteritems()
            })
        return output

    def get_string_multi(self, ids):
        entries = self.redis.mget('pm:i:{}'.format(id_) for id_ in ids)
        return dict(izip(ids, entries))
