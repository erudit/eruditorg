# -*- coding: utf-8 -*-

import logging

from requests.exceptions import ConnectionError

from .client import get_client
from .conf import settings as tracking_settings

logger = logging.getLogger(__name__)


def metric(metric_name, num=1, tags={}, **kwargs):
    """ Increments a specific metric.

    This function writes a point corresponding to a specific metric into an InfluxDB database. It
    can take additional keyword arguments that will be stored into the fields associated with the
    point being created.

    :param metric_name: The name of the metric to increment
    :param num: The number to increment the metric with (it defaults to 1)
    :param tags: The tags to store in the InfluxDB point
    :type metric_name: str
    :type num: int
    :type tags: dict

    """
    metric_fields = {'num': num}
    metric_fields.update(kwargs)
    metric_json_body = {
        'measurement': metric_name,
        'tags': tags,
        'fields': metric_fields,
    }
    try:
        assert tracking_settings.ACTIVATED
        client = get_client()
    except AssertionError:
        # The tracking is deactivated, so there's nothing else to do
        pass
    except ConnectionError:
        logger.error('InfluxDB server unavailable', exc_info=True)
    else:
        # Write the point into the InfluxDB database
        client.write_points([metric_json_body])
