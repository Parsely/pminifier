import testinstances
import unittest

class StoreTestBase(object):

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
        # Basic case
        id_ = self.store.get_id('test_string')
        self.assertEqual(id_, '0')
        # Test create_missing
        id_ = self.store.get_id('another_string', create_missing=False)
        self.assertIsNone(id_)

    def test_get_id_multi(self):
        # Basic case
        ids = self.store.get_id_multi(['test_string', 'another_string'])
        self.assertDictEqual(ids, {'another_string': '0', 'test_string': 'F'})
        # Test create_missing
        ids = self.store.get_id_multi(['test_string', 'notfound_string'],
                                           create_missing=False)
        self.assertDictEqual(ids, {'notfound_string': None,
                                   'test_string': 'F'})

    def test_get_string(self):
        # Not there yet
        self.assertIsNone(self.store.get_string(1))
        # Add and test again
        id_ = self.store.get_id('test_string')
        res = self.store.get_string(id_)
        self.assertEqual(res, 'test_string')

    def test_get_string_multi(self):
        # Not there yet
        ids = self.store.get_string_multi(['0', 'F'])
        self.assertDictEqual(ids, {'0': None, 'F': None})
        # Add and test again
        strings = ['test_string', 'another_string']
        ids = self.store.get_id_multi(strings)
        res = self.store.get_string_multi(ids.values())
        ids_inv = {v:k for k,v in ids.iteritems()} # change to {id: string}
        self.assertDictEqual(res, ids_inv)


if __name__ == '__main__':
    unittest.main()

