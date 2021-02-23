# -*- coding: utf-8 -*-

from influxdb import InfluxDBClient

from .conf import settings as metrics_settings

global _metrics_client
_metrics_client = None


def get_client(reset=False):
    """ Returns the InfluxDBClient instance to use to store tracking metrics. """
    global _metrics_client
    if _metrics_client is None or reset:
        client = InfluxDBClient(
            host=metrics_settings.INFLUXDB_HOST,
            port=metrics_settings.INFLUXDB_PORT,
            username=metrics_settings.INFLUXDB_USER,
            password=metrics_settings.INFLUXDB_PASSWORD,
            database=metrics_settings.INFLUXDB_DBNAME,
        )

        # Checks if the considered database already exists in order to know if we need to create it
        dbs = client.get_list_database()
        db_names = [db["name"] for db in dbs]
        if metrics_settings.INFLUXDB_DBNAME not in db_names:
            client.create_database(metrics_settings.INFLUXDB_DBNAME)

        _metrics_client = client

    return _metrics_client
