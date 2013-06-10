import atexit
import logging
import os
import shutil
import subprocess
import tempfile
import threading
import time

log = logging.getLogger(__name__)
running_instances = {} # keep track of what we've got
instance_tmpdir = tempfile.mkdtemp()

def _cleanup(exiting=False):
    """Stop all running instances and delete the temp dir"""
    global running_instances
    for instance in list(running_instances.values()):
        instance.terminate()
    running_instances = {}
    if exiting:
        shutil.rmtree(instance_tmpdir)
atexit.register(_cleanup, exiting=True)


class NotImplementedError(Exception):
    pass


class ManagedInstance(object):
    """Container for mongo/redis/whatever testing instances"""
    def __init__(self, name):
        if name in running_instances:
            raise Exception("Process %s is already running!", name)

        self._process = None
        self._root_dir = os.path.join(instance_tmpdir, name)

        self.conn = None
        self.log = logging.getLogger(name)
        self.logfile = os.path.join(instance_tmpdir, '%s.log' % name)
        self.name = name

        os.mkdir(self._root_dir)
        self._start_process()
        self._start_log_watcher()
        running_instances[self.name] = self

    def _start_log_watcher(self):
        """Watch the logfile and forward it to python logging"""
        logfile = open(self.logfile, 'r')
        def watcher():
            while True:
                line = logfile.readline().strip()
                if not line:
                    continue
                self.log.info(line)
        self._watch_thread = threading.Thread(target=watcher)
        self._watch_thread.daemon = True
        self._watch_thread.start()

    def _start_process(self):
        raise NotImplemetedError('nope, try a subclass')

    def flush(self):
        """Clear all data in underlying database"""
        raise NotImplementedError

    def get_logs(self):
        """Get the process's logs"""
        return open(self.logfile).read()

    def terminate(self):
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None
            shutil.rmtree(self._root_dir)
            os.remove(self.logfile)
        del running_instances[self.name]


class MongoInstance(ManagedInstance):
    """A managed mongo instance for testing"""
    def __init__(self, port, name='mongo'):
        """Start mongoinstance on the given port"""
        self.port = port
        super(MongoInstance, self).__init__('%s-%i' % (name, port))

    def _start_process(self):
        """Start the instance process"""
        import pymongo # localize dependencies
        log.info('Starting mongod on port %i...', self.port)
        self._process = subprocess.Popen(
            args=["mongod",
                  '--port', str(self.port),
                  '--bind_ip', '127.0.0.1',
                  '--dbpath', self._root_dir,
                  '--nojournal',
                  ],
            stderr=subprocess.STDOUT,
            stdout=open(self.logfile, 'w'),
            )

        # Connect to the shiny new instance
        self.conn = None
        fails = 0
        while self.conn is None:
            try:
                conn = pymongo.MongoClient(port=self.port)
                if conn.alive():
                    self.conn = conn
            except:
                if fails == 10:
                    break
                fails += 1
                time.sleep(1)

        if self.conn is None or self._process.poll() is not None:
            log.critical('Unable to start mongod in 10 seconds.')
            raise Exception("Unable to start mongod")

    def flush(self):
        """Flush all data in the db"""
        for dbname in self.conn.database_names():
            if dbname in ('local', 'admin', 'config'):
                self.conn.drop_database(dbname)


class RedisInstance(ManagedInstance):
    """A managed redis instance for testing"""
    def __init__(self, port, name='redis', dumpfile=None):
        """Start redis instance on the given port and inside root_dir"""
        self.port = port
        self.dumpfile = os.path.abspath(dumpfile) if dumpfile else None
        super(RedisInstance, self).__init__('%s-%i' % (name, port))


    def _start_process(self):
        """Start the instance process"""
        import redis # localize dependencies
        log.info('Starting redis-server on port %i...', self.port)
        if self.dumpfile:
            log.info('Loading dumpfile %s...', self.dumpfile)
            os.rename(
                self.dumpfile,
                os.path.join(self._root_dir, os.path.basename(self.dumpfile))
            )
        self._process = subprocess.Popen(
            args=["redis-server",
                  '--port', str(self.port),
                  '--bind', '127.0.0.1',
                  '--dir', self._root_dir,
                  ],
            stderr=subprocess.STDOUT,
            stdout=open(self.logfile, 'w'),
            )

        # Connect to the shiny new instance
        self.conn = None
        fails = 0
        while self.conn is None:
            try:
                conn = redis.StrictRedis(port=self.port)
                if conn.info()['loading'] == 0: # make sure dump is loaded
                    self.conn = conn
            except:
                if fails == 10:
                    break
                fails += 1
                time.sleep(1)

        if self.conn is None or self._process.poll() is not None:
            log.critical('Unable to start redis-server in 10 seconds')
            raise Exception("Unable to start redis-server")

    def flush(self):
        """Flush all data in all dbs"""
        self.conn.flushall()
