# - coding: utf-8 -
import unittest
import sys
import os

from pminifier.test.integration import PMinifierIntegrationTest
from pminifier.minifier import SimplerMinifier, Minifier

class SimplerMinifierTests(PMinifierIntegrationTest):
    def setUp(self):
        self.m = SimplerMinifier((self.cluster.mongo.conn, 'pminifier'),
                                 self.cluster.redis.conn,
                                 'groupkey')

    def test_retrieve_bad_urls(self):
        self.assertRaises(Minifier.DoesNotExist, self.m.get_string, "AfTea")

    def test_store_and_retrieve_same_url(self):
        o_id = self.m.get_id("http://www.youtube.com/")
        self.assertEqual(o_id, self.m.get_id("http://www.youtube.com/"))

    def test_counter(self):
        counter_value = self.m._get_current_counter_value()
        self.assertTrue(isinstance(counter_value, int))

    def test_cache_keys(self):
        try:
            self.m._cache_key_names('str', ['string based key'])
        except:
            self.fail('_cache_key_names threw an exception')

    def test_cache_key_unicode(self):
        try:
            self.m._cache_key_names('str', [u'nīcē ūnīcōde'])
        except:
            self.fail('_cache_key_names died on unicode')

    def test_store_and_retrieve_urls(self):
        urls_oid = []
        urls = ["http://google.com", "http://www.google.com",
                "https://mail.google.com/mail/u/0/#drafts",
                "https://www.google.com/#hl=en&output=search&sclient=psy-ab&q=parsely&qscrl=1&oq=parsely&aq=f&aqi=g-s4&aql=&gs_l=hp.3..0i10l4.2183l11396l0l11570l18l18l0l0l0l0l172l1787l10j8l18l0.frgbld.&pbx=1&bav=on.2,or.r_gc.r_pw.r_qf.,cf.osb&fp=3a4c3f9900aaf4a9&biw=1920&bih=982",
                "http://174.143.148.90/", "174.143.148.90",
                "potato", "potato"]
        for url in urls:
            url = unicode(url)
            o_id = self.m.get_id(url)
            self.assertEqual(url, self.m.get_string(o_id))
            # Check integrity of IDs
            urls_oid.append((o_id, url))
            for check_id, check_url in urls_oid:
                self.assertEqual(check_url, self.m.get_string(check_id))

if __name__ == '__main__':
    """Run the tests with caching enabled."""
    suite = unittest.TestSuite()
    for cache_hosts in [[], ['127.0.0.1']]:
        test = SimplerMinifierTests()
        suite.addTest(test)
    unittest.TextTestRunner(verbosity=2).run(suite)
