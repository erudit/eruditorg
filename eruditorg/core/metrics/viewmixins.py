# -*- coding: utf-8 -*-

from .metric import metric


class MetricCaptureMixin:
    """ This mixin create an InfluxDB point when the view is executed. """

    tracking_metric_name = None

    def capture_metric(self, response):
        """Given a response object, returns True if the metric should be captured.

        The default implementation returns True if the response's status code is 200.
        """
        return response.status_code == 200

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        response = super(MetricCaptureMixin, self).dispatch(request, *args, **kwargs)
        if self.capture_metric(response):
            self.incr_metric()
        return response

    def get_metric_fields(self):
        """ Returns the metric fields to embed in the point that will be created. """
        return {}

    def get_metric_tags(self):
        """ Returns the metric tags to embed in the point that will be created. """
        return {}

    def incr_metric(self):
        """ Increments the metric associated with the considered view. """
        if self.tracking_metric_name is None:  # pragma: no cover
            return
        metric(self.tracking_metric_name, tags=self.get_metric_tags(), **self.get_metric_fields())
