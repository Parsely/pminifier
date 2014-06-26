import testinstances
import unittest

from pminifier.storage.redisstore import RedisStore
from tests.pminifier.storage import StoreTestBase

class RedisStoreTests(StoreTestBase, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mongo = testinstances.RedisInstance(10001)

    def setUp(self):
        self.mongo.flush()
        self.store = RedisStore({'port': 10001})


if __name__ == '__main__':
    unittest.main()
