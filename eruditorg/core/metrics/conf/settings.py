# -*- coding: utf-8 -*-

from django.conf import settings


INFLUXDB_HOST = getattr(settings, 'TRACKING_INFLUXDB_HOST', 'localhost')
INFLUXDB_PORT = getattr(settings, 'TRACKING_INFLUXDB_PORT', 8086)
INFLUXDB_DBNAME = getattr(settings, 'TRACKING_INFLUXDB_DBNAME', 'erudit-metrics')
INFLUXDB_USER = getattr(settings, 'TRACKING_INFLUXDB_USER', 'root')
INFLUXDB_PASSWORD = getattr(settings, 'TRACKING_INFLUXDB_PASSWORD', 'root')

# This setting can be used to deactivate the tracking. It will silent any error that could be logged
# if the InfluxDB server is not reachable.
ACTIVATED = getattr(settings, 'TRACKING_ACTIVATED', True)
