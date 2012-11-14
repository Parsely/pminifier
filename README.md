pminifier
=========
The minifier maintains a collection of URL/ID pairs, to allow for 'shortening' a URL and fast access to it. Example: 

`` http://www.google.com/  --->  3294 ``

Lookups are ither by URL or ID.

The ``Minifier`` object saves and reads a URL/ID pair in a mongdb database. If the URL is not found , it's automatically created.

The ``CachedMinifier`` object is a ``Minifier`` that uses a cache (``Memcached`` or ``Redis``) to perform faster reads when looking up a URL or ID.

Usage
-----

      from pminifier.minifier import CachedMinifier
      from pminifier.redis_cache_backend import RedisCacheBackend, cached as cache_decorator
      cache = RedisCacheBackend(host='localhost')
      minifier = CachedMinifier('localhost', 'minified_urls', cache, cache_decorator)
      minifier.get_id("http://google.com", "test")
