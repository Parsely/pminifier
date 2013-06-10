import logging
import os
import pymongo
import redis
import shutil
import subprocess
import tempfile
import threading
import time

from pminifier.test import instances

log = logging.getLogger(__name__)
_cluster = None

def get_global_cluster():
    global _cluster
    if _cluster is None:
        _cluster = PMinifierCluster()
    return _cluster


class PMinifierCluster(object):
    """Manage the set of pminifier databases used in integration tests."""
    def __init__(self):
        self.temp_dir = instances.instance_tmpdir
        self.mongo = instances.MongoInstance(10001)
        self.redis = instances.RedisInstance(10101)

    def flush(self):
        """Flush all data in the cluster"""
        self.mongo.flush()
        self.redis.flush()

    def terminate(self):
        """Stop all processes and delete temp dir"""
        global _cluster
        if not self.mongo and not self.redis:
            return # already dead

        self.mongo.terminate()
        self.redis.terminate()
        self.mongo = None
        self.redis = None
        _cluster = None

    def restart_redis(self, dumpfile=None):
        """Restart redis, optionally with a dumpfile loaded"""
        self.redis.terminate()
        self.redis = instances.RedisInstance(10101, dumpfile=dumpfile)
