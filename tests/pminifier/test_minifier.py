import mock
import testinstances
import unittest

from pminifier import Minifier

class MinifierTests(unittest.TestCase):
    """Full integration tests for mongo, redis, and the LRU"""

    @classmethod
    def setUpClass(cls):
        cls.mongo = testinstances.MongoInstance(10101)
        cls.redis = testinstances.RedisInstance(10001)

    def setUp(self):
        self.mongo.flush()
        self.redis.flush()
        self.backends = [mock.MagicMock(), mock.MagicMock()]
        self.minifier = Minifier(self.backends)

    def test_get_id_multi(self):
        # Test the first backend having the result
        self.backends[0].get_id_multi.return_value = {'test': 1}
        self.assertEqual(self.minifier.get_id_multi(['test']), {'test': 1})
        self.assertTrue(self.backends[0].get_id_multi.called)
        self.assertFalse(self.backends[1].get_id_multi.called)
        self.backends[0].reset_mock()

        # Test the second backend having/creating it
        self.backends[0].get_id_multi.return_value = {'test': None}
        self.backends[1].get_id_multi.return_value = {'test': 2}
        self.assertEqual(self.minifier.get_id_multi(['test']), {'test': 2})
        self.assertTrue(self.backends[0].get_id_multi.called)
        self.assertTrue(self.backends[1].get_id_multi.called)
        self.assertTrue(self.backends[0].cache_id_results.called)

    def test_get_string_multi(self):
        self.backends[0].get_string_multi.return_value = {1: 'test'}
        self.assertEqual(self.minifier.get_string_multi([1]), {1: 'test'})
        self.assertTrue(self.backends[0].get_string_multi.called)
        self.assertFalse(self.backends[1].get_string_multi.called)
        self.backends[0].reset_mock()

        # Test the second backend having/creating it
        self.backends[0].get_string_multi.return_value = {2: None}
        self.backends[1].get_string_multi.return_value = {2: 'test'}
        self.assertEqual(self.minifier.get_string_multi('test'), {2: 'test'})
        self.assertTrue(self.backends[0].get_string_multi.called)
        self.assertTrue(self.backends[1].get_string_multi.called)
        self.assertTrue(self.backends[0].cache_string_results.called)


if __name__ == '__main__':
    unittest.main()
