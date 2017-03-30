"""Metrics client using Prometheus Push Gateway"""
import prometheus_client as pc


class PrometheusMetrics(object):

    def __init__(self, run):
        if run:
            pc.start_http_server(8000)

        self.eval_timer = pc.Summary('loop_time_seconds', 'Time to evaluate services')
