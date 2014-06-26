import testinstances
import unittest

from pminifier.storage.mongostore import MongoStore
from tests.pminifier.storage import StoreTestBase

class MongoStoreTests(StoreTestBase, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mongo = testinstances.MongoInstance(10101)

    def setUp(self):
        self.mongo.flush()
        self.store = MongoStore({'port': 10101}, 'test_db')

    def test_cache_get_id_multi(self):
        self.assertRaises(
            NotImplementedError,
            lambda: self.store.cache_get_id_multi({'test_string': '0',
                                                   'another_string': 'F'}),
        )

    def test_cache_get_string_multi(self):
        self.assertRaises(
            NotImplementedError,
            lambda: self.store.cache_get_string_multi({'0': 'test_string',
                                                       'F': 'another_string'})
        )


if __name__ == '__main__':
    unittest.main()
