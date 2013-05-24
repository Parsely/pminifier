from cache import CacheBackend
import redis
import md5
import cPickle as pickle

class RedisCacheBackend(CacheBackend):
    def __init__(self,params):
        self.timeout = params.get('timeout', 3600)
        host = params.get('host', 'localhost')
        port = params.get('port', 6379)
        self.client = redis.Redis(host,port)
        
    def get(self, key):
        value = self.client.get(key)
        if not value:
            return None
        return pickle.loads(value)

    def get_all(self, keys):
        values = self.client.mget(keys)
        return [(pickle.loads(value) if value else None) for value in values]

    def set(self, key, value):
        if self.timeout:
            self.client.set(key, pickle.dumps(value))
            self.client.expire(key, self.timeout)
        else:
            self.client.set(key, pickle.dumps(value))

    def delete(self, key):
         self.client.delete(key)

    def clear(self):
        self.client.flushdb()

class cached(object):
    """ This decorator wraps methods and caches their results"""
    def __init__(self,client):
        self.client = client
        
    def _cache_key(self, func, args, kw):
        classname = args[0].__class__.__name__
        funcname = func.__name__
        mangled_args = str(args)+str(kw)
        key = "%s:%s:%s" % (classname,funcname,md5.md5(mangled_args).hexdigest())
        return key

    def __call__(self, func):
        def _wrapped(*args,**kw):
            cacheclient = self.client
            key = self._cache_key(func, args,kw)
            data = cacheclient.get(key)
            if data is None:
                data = func(*args,**kw)
                cacheclient.set(key, data)
            return data

        return _wrapped
