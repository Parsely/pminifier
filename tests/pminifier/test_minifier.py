import unittest
import sys
import os

from pminifier.test.integration import PMinifierIntegrationTest
from pminifier.minifier import Minifier

class MinifierIntegrationTests(PMinifierIntegrationTest):
    def __init__(self, *args, **kwargs):
        super(MinifierIntegrationTests, self).__init__(*args, **kwargs)

    def setUp(self):
        self.m = Minifier(self.cluster.mongo.conn, 'pminifier')

    def test_int_to_base62(self):
        self.assertEqual('LfqqC7n0s', self.m.int_to_base62(9999999999999999))
        self.assertEqual('0U', self.m.int_to_base62(3294))
        self.assertEqual('Fq', self.m.int_to_base62(99))
        self.assertRaises(ValueError, self.m.int_to_base62, -1)
        self.assertRaises(TypeError, self.m.int_to_base62, "chipmunks")

    def test_base62_to_int(self):
        self.assertEqual(9999999999999999, self.m.base62_to_int('LfqqC7n0s'))
        self.assertEqual(3294, self.m.base62_to_int('0U'))
        self.assertEqual(99, self.m.base62_to_int('Fq'))

    def test_retrieve_bad_urls(self):
        self.assertRaises(Minifier.DoesNotExist, self.m.get_string, 9001)

    def test_store_and_retrieve_same_url(self):
        o_id = self.m.get_id("http://www.youtube.com/", 'test')
        self.assertEqual(o_id, self.m.get_id("http://www.youtube.com/", 'test'))

    def test_store_and_retrieve_urls(self):
        urls_oid = []
        urls = ["http://google.com", "http://www.google.com",
                "https://mail.google.com/mail/u/0/#drafts",
                "https://www.google.com/#hl=en&output=search&sclient=psy-ab&q=parsely&qscrl=1&oq=parsely&aq=f&aqi=g-s4&aql=&gs_l=hp.3..0i10l4.2183l11396l0l11570l18l18l0l0l0l0l172l1787l10j8l18l0.frgbld.&pbx=1&bav=on.2,or.r_gc.r_pw.r_qf.,cf.osb&fp=3a4c3f9900aaf4a9&biw=1920&bih=982",
                "http://174.143.148.90/", "174.143.148.90",
                "potato", "potato"]
        for url in urls:
            url = unicode(url)
            o_id = self.m.get_id(url, 'test')
            self.assertEqual(url, self.m.get_string(o_id))
            # Check integrity of IDs
            urls_oid.append((o_id, url))
            for check_id, check_url in urls_oid:
                self.assertEqual(check_url, self.m.get_string(check_id))

if __name__ == '__main__':
    """Run the tests with and without memcached/caching enabled."""
    suite = unittest.TestSuite()
    for cache_hosts in [[], ['127.0.0.1']]:
        test = MinifierIntegrationTests()
        suite.addTest(test)
    unittest.TextTestRunner(verbosity=2).run(suite)
