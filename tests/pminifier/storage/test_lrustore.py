import unittest

from pminifier.storage.lrustore import LRUStore

class LRUStoreTests(unittest.TestCase):

    def setUp(self):
        self.store = LRUStore(1000)

    def test_cache_get_id_multi(self):
        self.store.cache_get_id_multi({'test_string': '0',
                                       'another_string': 'F'})
        # Test getting by string
        res = self.store.get_id_multi(['test_string', 'another_string'], create_missing=False)
        self.assertDictEqual(res, {'test_string': '0','another_string': 'F'})
        # Test gettng by ID
        res = self.store.get_string_multi(['0', 'F'])
        self.assertDictEqual(res, {'0': 'test_string', 'F': 'another_string'})

    def test_cache_get_string_multi(self):
        self.store.cache_get_string_multi({'0': 'test_string',
                                           'F': 'another_string'})
        # Test getting by string
        res = self.store.get_id_multi(['test_string', 'another_string'], create_missing=False)
        self.assertDictEqual(res, {'test_string': '0','another_string': 'F'})
        # Test gettng by ID
        res = self.store.get_string_multi(['0', 'F'])
        self.assertDictEqual(res, {'0': 'test_string', 'F': 'another_string'})

    def test_get_id(self):
        # Basic test
        self.store.lru[('s', 'test_string')] = 'foo'
        self.assertEqual(self.store.get_id('test_string'), 'foo')
        # Test create_missing
        id_ = self.store.get_id('another_string', create_missing=False)
        self.assertIsNone(id_)

    def test_get_id_multi(self):
        # Basic test
        self.store.lru[('s', 'test_string')] = 'foo'
        self.store.lru[('s', 'another_string')] = 'bar'
        self.assertDictEqual(
            self.store.get_id_multi(['test_string', 'another_string']),
            {'test_string': 'foo', 'another_string': 'bar'}
        )
        # Test create_missing
        ids = self.store.get_id_multi(['test_string', 'notfound_string'],
                                      create_missing=False)
        self.assertDictEqual(ids, {'test_string': 'foo',
                                   'notfound_string': None})

    def test_get_string(self):
        # Not there yet
        self.assertIsNone(self.store.get_string(1))
        # Add and test again
        self.store.lru[('i', 'foo')] = 'test_string'
        res = self.store.get_string('foo')
        self.assertEqual(res, 'test_string')

    def test_get_string_multi(self):
        # Not there yet
        ids = self.store.get_string_multi(['foo', 'bar'])
        self.assertDictEqual(ids, {'foo': None, 'bar': None})
        # Add and test again
        self.store.lru[('i', 'foo')] = 'test_string'
        self.store.lru[('i', 'bar')] = 'another_string'
        res = self.store.get_string_multi(ids.keys())
        self.assertDictEqual(res, {'foo': 'test_string',
                                   'bar': 'another_string'})


if __name__ == '__main__':
    unittest.main()
