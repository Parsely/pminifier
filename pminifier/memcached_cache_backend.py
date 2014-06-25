import md5
import pylibmc

from pylru import lrudecorator

from cache import CacheBackend

class MemcachedCacheBackend(CacheBackend):
    def __init__(self,params):
        self.timeout = params.get('timeout', 3600)
        host = params.get('host', ['localhost'])
        self.client = pylibmc.Client(host, binary=True)

    def set(self, key, value):
        self.client.set(key,value,self.timeout)

    def get(self,key):
        return self.client.get(key)

    def delete(self, key):
        self.client.delete(key)

    def clear(self):
        self.client.flush_all()

class cached(object):
    """ This decorator wraps methods and caches their results with memcached. """
    def __init__(self,client):
        self.client = client

    def _cache_key(self, func, args,kw):
        classname = args[0].__class__.__name__
        funcname = func.__name__
        mangled_args = str(args)+str(kw)
        key = "%s:%s:%s" % (classname,funcname,md5.md5(mangled_args).hexdigest())
        return key

    def __call__(self, func):
        def wrapped(*args,**kw):
            memcached = self.client
            key = self._cache_key(func, args,kw)
            data = memcached.get(key)
            if data is None:
                data = func(*args,**kw)
                memcached.set(key, data)
            return data
        return wrapped
