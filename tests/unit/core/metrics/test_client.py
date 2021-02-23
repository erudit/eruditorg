# -*- coding: utf-8 -*-

import unittest.mock

from django.test import TestCase
from influxdb import InfluxDBClient

from core.metrics.client import get_client


class TestGetClient(TestCase):
    @unittest.mock.patch.object(InfluxDBClient, "get_list_database")
    @unittest.mock.patch.object(InfluxDBClient, "create_database")
    def test_can_return_an_influxdb_client_and_create_the_database(
        self, mock_list_db, mock_create_db
    ):
        # Run & check
        get_client(reset=True)
        self.assertTrue(mock_create_db.call_count, 1)
