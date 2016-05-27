# -*- coding: utf-8 -*-

from influxdb import InfluxDBClient

from .conf import settings as tracking_settings


_tracking_client = None


def get_client():
    """ Returns the InfluxDBClient instance to use to store tracking metrics. """
    if _tracking_client is None:
        global _tracking_client

        client = InfluxDBClient(
            host=tracking_settings.INFLUXDB_HOST, port=tracking_settings.INFLUXDB_PORT,
            username=tracking_settings.INFLUXDB_USER, password=tracking_settings.INFLUXDB_PASSWORD,
            database=tracking_settings.INFLUXDB_DBNAME)

        # Checks if the considered database already exists in order to know if we need to create it
        dbs = client.get_list_database()
        db_names = [db['name'] for db in dbs]
        if tracking_settings.INFLUXDB_DBNAME not in db_names:
            client.create_database(tracking_settings.INFLUXDB_DBNAME)

        _tracking_client = client

    return _tracking_client
