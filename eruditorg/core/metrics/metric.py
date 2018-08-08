# -*- coding: utf-8 -*-

import structlog

from requests.exceptions import ConnectionError

from .client import get_client
from .conf import settings as metrics_settings

logger = structlog.getLogger(__name__)


def metric(metric_name, num=1, time=None, tags={}, **kwargs):
    """ Increments a specific metric.

    This function writes a point corresponding to a specific metric into an InfluxDB database. It
    can take additional keyword arguments that will be stored into the fields associated with the
    point being created.

    :param metric_name: The name of the metric to increment
    :param num: The number to increment the metric with (it defaults to 1)
    :param time: The datetime associated with the metric event
    :param tags: The tags to store in the InfluxDB point
    :type metric_name: str
    :type num: int
    :type time: datetime
    :type tags: dict

    """
    metric_fields = {'num': num}
    metric_fields.update(kwargs)
    metric_json_body = {
        'measurement': metric_name,
        'tags': tags,
        'fields': metric_fields,
    }

    if time:
        metric_json_body.update({'time': time})

    try:
        assert metrics_settings.ACTIVATED
        client = get_client()
        # Write the point into the InfluxDB database
        client.write_points([metric_json_body])
    except AssertionError:
        # The tracking is deactivated, so there's nothing else to do
        pass
    except ConnectionError:
        logger.error('configuration.error', msg="InfluxDB server unavailable")
