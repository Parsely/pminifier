"""
Maintain a collection of URL/ID pairs, to allow for 'shortening' a URL.
    Ex: http://www.google.com/  --->  3294
    Also allow for URLs to be represented as a url friendly string.
        Ex: 329423322  --->  'cZ1Ya'

        Unit tests can be found in minifier_tests.py
"""
import pymongo
import math
import md5

import logging
from pymongo.errors import OperationFailure
from pylru import lrudecorator

log = logging.getLogger('pminifier')

class Minifier(object):
    alphabet = '2FQYNEJAUsbGu41zndZTeocMai5H7OIjXkKg8qyt3WC9hLplxfVBm0wSRr6vPD'
    
    class DoesNotExist(Exception):
        "The requested URL does not exist in the table."

    def __init__(self, mongo_host, mongo_db, cache_client):
        self.conn = pymongo.Connection(mongo_host)
        self.db = self.conn[mongo_db]
        self._init_mongo()
        self.client = cache_client
       
    def _init_mongo(self):
        """Initialize mongo indexes and sharding."""
        # Index only when necessary. Many attempts to make the same index
        # at the same moment (from a migration for example) causes mongo
        # to throw confusing errors
        index = [('url', 1)]
        indexes = self.db.urlById.index_information()
        indexes = [i['key'] for i in indexes.values()]
        if index not in indexes:
            log.warning('Creating urlById index')
            self.db.urlById.ensure_index(index, background=False)

        # Only way to check if we're in a sharded environment
        try:
            self.db.command({'isdbgrid': 1})
        except OperationFailure as ex:
            return # nope

        db_info = self.conn.config.databases.find_one({'_id': self.db.name})
        if not db_info or not db_info['partitioned']:
            self.conn.admin.command({"enablesharding": self.db.name})

        fullname = '%s.%s' % (self.db.name, 'urlById')
        coll_info = self.conn.config.collections.find_one({'_id': fullname})
        if not coll_info or 'key' not in coll_info:
            self.conn.admin.command({'shardcollection': fullname,
                                     'key': {'_id': 1}})
        
    def get_id(self, url, groupkey):
        """Returns the minified ID of the url"""
        return self._get(url, groupkey, as_str=True)
    
    def _get(self, url, groupkey, as_str=False):
        if not url:
            return None
        entries = self.db.urlById.find({'url': url}, fields=['_id', 'groupkey'])
        entries = [e for e in entries if e.get('groupkey') == groupkey]
        if entries:
            return self.int_to_base62(entries[0]['_id']) if as_str else entries[0]['_id']

        # Create new entry if not found
        counter = self.db.urlByIdMeta.find_and_modify(query={'_id': 'minifier_counter'},
                                                      update={'$inc': {'value': 1}},
                                                      upsert=True, new=True)
        self.db.urlById.insert({'_id': counter['value'],
                                'url': url,
                                'groupkey': groupkey}, safe=True)
        return self.int_to_base62(counter['value']) if as_str else counter['value']

    def get_string(self, id):
        """Looks up the string by its ID (minified or integer form)"""
        if isinstance(id, basestring):
            entry = self.db.urlById.find_one({'_id': self.base62_to_int(id)}, fields=['url'])
        else:
            entry = self.db.urlById.find_one({'_id': id}, fields=['url'])

        if not entry:
            raise Minifier.DoesNotExist('The URL provided does not exist ' +
                                        'in the minification table.')
        return entry['url']

    def int_to_base62(self, id):
        """Convert the int id to a user-friendly string using base62"""
        if id < 0:
            raise ValueError("Must supply a positive integer.")
        l = len(self.alphabet)
        converted = []
        while id != 0:
            id, r = divmod(id, l)
            converted.insert(0, self.alphabet[r])
        return "".join(converted) or '0'

    def base62_to_int(self, minified):
        """Convert the base62 string back to an int"""
        if set(minified) - set(self.alphabet):
            raise ValueError("Minified ID contains invalid characters '%s'" % "".join(set(minified) - set(self.alphabet)))

        s = minified[::-1]
        l = len(self.alphabet)
        output = 0
        for i, c in enumerate(s):
            output += self.alphabet.index(c) * math.pow(l, i)
        return int(output)

class CachedMinifier(Minifier):
    """
    Minifier that caches its operations through a user-defined decorator
    """
    def __init__(self,
                 mongo_host,
                 mongo_db,
                 cache_client,
                 cache_decorator_class,
                 lrusize=500):
        super(CachedMinifier,self).__init__(mongo_host, mongo_db, cache_client)
        lrucache = lrudecorator(lrusize)
        dec = cache_decorator_class(cache_client)

        self.base62_to_int = lrucache(dec(self.base62_to_int))
        self.int_to_base62 = lrucache(dec(self.int_to_base62))
        self.get_string = lrucache(dec(self.get_string))
        self.get_id = lrucache(dec(self.get_id))
