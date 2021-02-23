# -*- coding: utf-8 -*-

import datetime as dt
import unittest.mock

from django.test import TestCase
from influxdb import InfluxDBClient

from core.metrics.conf import settings as metrics_settings
from core.metrics.metric import metric


_test_points = []


def fake_write_points(points):
    global _test_points
    _test_points.extend(points)


class TestMetric(TestCase):
    def tearDown(self):
        super(TestMetric, self).tearDown()
        global _test_points
        _test_points = []

    @unittest.mock.patch.object(InfluxDBClient, "get_list_database")
    @unittest.mock.patch.object(InfluxDBClient, "create_database")
    @unittest.mock.patch.object(InfluxDBClient, "write_points")
    def test_can_increment_a_simple_metric(self, mock_write_points, mock_list_db, mock_create_db):
        # Setup
        mock_write_points.side_effect = fake_write_points
        # Run
        metric("test__metric")
        # Check
        global _test_points
        self.assertEqual(
            _test_points, [{"tags": {}, "fields": {"num": 1}, "measurement": "test__metric"}]
        )

    @unittest.mock.patch.object(InfluxDBClient, "get_list_database")
    @unittest.mock.patch.object(InfluxDBClient, "create_database")
    @unittest.mock.patch.object(InfluxDBClient, "write_points")
    def test_can_increment_a_simple_metric_by_a_specific_number(
        self, mock_write_points, mock_list_db, mock_create_db
    ):
        # Setup
        mock_write_points.side_effect = fake_write_points
        # Run
        metric("test__metric", num=4)
        # Check
        global _test_points
        self.assertEqual(
            _test_points, [{"tags": {}, "fields": {"num": 4}, "measurement": "test__metric"}]
        )

    @unittest.mock.patch.object(InfluxDBClient, "get_list_database")
    @unittest.mock.patch.object(InfluxDBClient, "create_database")
    @unittest.mock.patch.object(InfluxDBClient, "write_points")
    def test_can_increment_a_simple_metric_by_specifying_a_specific_time(
        self, mock_write_points, mock_list_db, mock_create_db
    ):
        # Setup
        mock_write_points.side_effect = fake_write_points
        nowd = dt.datetime.now()
        # Run
        metric("test__metric", time=nowd)
        # Check
        global _test_points
        self.assertEqual(
            _test_points,
            [
                {
                    "tags": {},
                    "fields": {"num": 1},
                    "measurement": "test__metric",
                    "time": nowd,
                }
            ],
        )

    @unittest.mock.patch.object(InfluxDBClient, "get_list_database")
    @unittest.mock.patch.object(InfluxDBClient, "create_database")
    @unittest.mock.patch.object(InfluxDBClient, "write_points")
    def test_do_nothing_if_the_metrics_capturing_is_deactivated(
        self, mock_write_points, mock_list_db, mock_create_db
    ):
        # Setup
        mock_write_points.side_effect = fake_write_points
        metrics_settings.ACTIVATED = False
        # Run
        metric("test__metric")
        # Check
        global _test_points
        self.assertFalse(len(_test_points))
        metrics_settings.ACTIVATED = True

    def test_do_not_raise_in_case_of_connection_error(self):
        # Run
        metric("test__metric")
        # Check
        global _test_points
        self.assertFalse(len(_test_points))
