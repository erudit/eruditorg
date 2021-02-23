# -*- coding: utf-8 -*-

from django.conf import settings


INFLUXDB_HOST = getattr(settings, "METRICS_INFLUXDB_HOST", "localhost")
INFLUXDB_PORT = getattr(settings, "METRICS_INFLUXDB_PORT", 8086)
INFLUXDB_DBNAME = getattr(settings, "METRICS_INFLUXDB_DBNAME", "erudit-metrics")
INFLUXDB_USER = getattr(settings, "METRICS_INFLUXDB_USER", "root")
INFLUXDB_PASSWORD = getattr(settings, "METRICS_INFLUXDB_PASSWORD", "root")

# This setting can be used to deactivate capturing metrics. It will silent any error that could be
# logged if the InfluxDB server is not reachable.
ACTIVATED = getattr(settings, "METRICS_ACTIVATED", False)
