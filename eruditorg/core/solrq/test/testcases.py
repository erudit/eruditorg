# -*- coding: utf-8 -*-

import os.path as op
import unittest

import pysolr


FIXTURE_ROOT = op.join(op.dirname(__file__), 'fixtures')


class SolrqTestCase(unittest.TestCase):
    def setUp(self):
        super(SolrqTestCase, self).setUp()
        self.client = pysolr.Solr('http://dummy.test', timeout=10)
