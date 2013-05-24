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
        if isinstance(mongo_host, basestring) or isinstance(mongo_host, list):
            self.conn = pymongo.Connection(mongo_host)
        else:
            self.conn = mongo_host
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
        res = self._get_id_multi([url], groupkey, as_str=True)
        return res[url] if res else None

    def get_multiple_ids(self, urls, groupkey):
        """Returns the minified ID of the url"""
        return self._get_id_multi(urls, groupkey, as_str=True)

    def _get_id_multi(self, urls, groupkey, as_str=False):
        if not urls:
            return None

        entries = self.db.urlById.find({'url': {'$in':urls}}, fields=['_id', 'groupkey','url'])
        entries = [e for e in entries if e.get('groupkey') == groupkey]
        found = set([entry['url'] for entry in entries])
        notfound = set(urls) - set(found)

        res = {}
        for entry in entries:
            res[entry['url']] = self.int_to_base62(entry['_id']) if as_str else entry[0]['_id']

        if len(notfound) == 0:
            return res

        # Create new entry for keys not found
        for url in notfound:
            counter = self.db.urlByIdMeta.find_and_modify(query={'_id': 'minifier_counter'},
                                                          update={'$inc': {'value': 1}},
                                                          upsert=True, new=True)
            self.db.urlById.insert({'_id': counter['value'],
                                    'url': url,
                                    'groupkey': groupkey}, safe=True)
            
            value = self.int_to_base62(counter['value']) if as_str else counter['value']
            res[url] = value
            
        return res

    def get_multiple_strings(self, ids):
        """Looks up the string by its IDs (minified or integer form)"""  
        converted = {}
        for id in ids:
            if isinstance(id, basestring):
                converted[self.base62_to_int(id)] = id 
            else:
                converted[id] = id

        criteria = {'_id':{'$in':converted.keys()}}
        entries = self.db.urlById.find(criteria, fields=['url'])
        res = {}

        for entry in entries:
            res[converted[ entry['_id'] ]] = entry['url']
        
        notfound = set(converted.values()) - set(res.keys())
        for url in notfound:
            res[url] = None

        return res

    def get_string(self, id):
        """Looks up the string by its ID (minified or integer form)"""
        res = self.get_multiple_strings([id])
        if not res:
                raise Minifier.DoesNotExist('The URL provided does not exist ' +
                                            'in the minification table.')
        return res[id]

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

        self._uncached_get_string = self.get_string
        self._uncached_get_id = self.get_id
        
        self.get_string = lrucache(dec(self.get_string))
        self.get_id = lrucache(dec(self.get_id))

        self.dec = dec


    def get_multiple_ids(self, urls, groupkey):
        single_item_func = self._uncached_get_id
        cached_ids = self._get_from_cache(single_item_func, urls, [groupkey])
        uncached_urls = set(urls) - set(cached_ids.keys())
        uncached_ids = super(CachedMinifier, self).get_multiple_ids(uncached_urls,
                                                                    groupkey)
        self._set_in_cache(single_item_func, uncached_ids, [groupkey])
        cached_ids.update(uncached_ids)

        return cached_ids


    def get_multiple_strings(self, ids):
        single_item_func = self._uncached_get_string
        cached_strings = self._get_from_cache(single_item_func, ids)
        uncached_ids = set(ids) - set(cached_strings.keys())
        uncached_strings = super(CachedMinifier,
                                 self).get_multiple_strings(uncached_ids)
        self._set_in_cache(single_item_func, uncached_strings)
        cached_strings.update(uncached_strings)

        return cached_strings


    def _get_key(self, single_item_func, item, more_args):
        if more_args:
            args = tuple([item] + more_args)
        else:
            args = (item,)
        key = self.dec._cache_key(single_item_func, args, {})
        return key


    def _get_from_cache(self, single_item_func, items, more_args=None):
        datas = {}
        for item in items:
            key = self._get_key(single_item_func, item, more_args)
            data = self.client.get(key)
            if data:
                datas.setdefault(item, data)
        return datas


    def _set_in_cache(self, single_item_func, results, more_args=None):
        for item in results:
            res = results[item]
            key = self._get_key(single_item_func, item, more_args)
            self.client.set(key, res)
