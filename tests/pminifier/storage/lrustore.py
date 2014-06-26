import unittest

from pminifier.storage.lrustore import LRUStore
from tests.pminifier.storage import StoreTestBase

class LRUStoreTests(StoreTestBase, unittest.TestCase):

    def setUp(self):
        self.store = LRUStore(1000)


if __name__ == '__main__':
    unittest.main()

