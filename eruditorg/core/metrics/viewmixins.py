# -*- coding: utf-8 -*-

from .metric import metric


class MetricCaptureMixin(object):
    """ This mixin create an InfluxDB point when the view is executed. """
    tracking_metric_name = None

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        response = super(MetricCaptureMixin, self).dispatch(request, *args, **kwargs)
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
        if self.tracking_metric_name is None:
            return
        metric(self.tracking_metric_name, tags=self.get_metric_tags(), **self.get_metric_fields())
