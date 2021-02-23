# -*- coding: utf-8 -*-

import unittest.mock

from django.http import HttpResponse
from django.test import RequestFactory
from django.test import TestCase
from django.views.generic import View
from influxdb import InfluxDBClient

from core.metrics.viewmixins import MetricCaptureMixin


_test_points = []


def fake_write_points(points):
    global _test_points
    _test_points.extend(points)


class TestMetricCaptureMixin(TestCase):
    def setUp(self):
        super(TestMetricCaptureMixin, self).setUp()
        self.factory = RequestFactory()

    def tearDown(self):
        super(TestMetricCaptureMixin, self).tearDown()
        global _test_points
        _test_points = []

    @unittest.mock.patch.object(InfluxDBClient, "get_list_database")
    @unittest.mock.patch.object(InfluxDBClient, "create_database")
    @unittest.mock.patch.object(InfluxDBClient, "write_points")
    def test_can_write_a_metric_each_time_the_view_is_executed(
        self, mock_write_points, mock_list_db, mock_create_db
    ):
        # Setup
        class MyView(MetricCaptureMixin, View):
            tracking_metric_name = "test__metric"

            def get(self, request):
                return HttpResponse()

        mock_write_points.side_effect = fake_write_points

        request = self.factory.get("/")
        view = MyView.as_view()

        # Run
        view(request)

        # Check
        global _test_points
        self.assertEqual(
            _test_points, [{"tags": {}, "fields": {"num": 1}, "measurement": "test__metric"}]
        )
