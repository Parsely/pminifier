pminifier
=========
The minifier maintains a collection of URL/ID pairs, to allow for 'shortening' a URL and fast access to it. Example: 

`` http://www.google.com/  --->  3294 ``

Lookups are ither by URL or ID.

The ``Minifier`` object saves and reads a URL/ID pair in a mongdb database. 

The ``CachedMinifier`` object is a ``Minifier`` that uses a cache (``Memcached`` or ``Redis``) to perform faster reads when looking up a URL or ID.