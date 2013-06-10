import datetime
import json
import logging
import os
import shutil
import subprocess
import unittest
import pandas
import testconfig

from distutils import dir_util

from pminifier.test.cluster import get_global_cluster

log = logging.getLogger(__name__)

class FixtureLoadingError(Exception):
    pass

class PMinifierIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        get_global_cluster() # make sure everything is started

    @classmethod
    def tearDownClass(cls):
        get_global_cluster().flush()

    @property
    def cluster(self):
        return get_global_cluster()

    def setUp(self):
        get_global_cluster() # make sure everything is started


    def tearDown(self):
        self.cluster.flush()
