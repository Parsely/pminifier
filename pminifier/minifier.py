import logging
import math
import md5
import time

log = logging.getLogger('pminifier')

class Minifier(object):

    def __init__(self, storage_backends):
        """Create a new Minifier.

        :param storage_backends: An iterable of
            :class:`pminifier.storage.StorageBase` used
            to store and look up minified IDs
        """
        self._backends = list(storage_backends) # exhausted iterables suck

    def _get_id_multi(self, strings, backends, create_missing):
        """Recursively get IDs so early backends can cache the result."""
        # We create IDs only for the last backend and if create_missing=True
        do_create = len(backends) == 1 and create_missing
        output = backends[0].get_id_multi(strings, create_missing=do_create)
        # If there are more backends to try, keep going down the list
        missing = [s for s in strings if output.get(s) is None]
        if len(backends) > 1 and missing:
            found = self._get_id_multi(missing, backends[1:], create_missing)
            backends[0].cache_id_results(found)
            output.update(found)
        return output

    def get_id(self, string, create_missing=False):
        return self.get_id_multi(
            [string],
            create_missing=create_missing
        ).get(string)

    def get_id_multi(self, strings, create_missing=False):
        return self._get_id_multi(strings, self._backends, create_missing)

    def _get_string_multi(self, ids, backends):
        """Recursively get strings so backend can cache results."""
        output = backends[0].get_string_multi(ids)
        # If there are more backends to try, keep going down the list
        missing = [i for i in ids if output.get(i) is None]
        if len(backends) > 1 and missing:
            found = self._get_string_multi(missing, backends[1:])
            backends[0].cache_string_results(found)
            output.update(found)
        return output

    def get_string(self, id):
        return self.get_string_multi([id]).get(id)

    def get_string_multi(self, ids):
        return self._get_string_multi(ids, self._backends)
