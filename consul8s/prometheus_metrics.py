"""Metrics client using Prometheus Push Gateway"""
import prometheus_client as pc


class PrometheusMetrics(object):

    def __init__(self, location):
        self._location = location
        self._registry = pc.CollectorRegistry()

    def push_and_clear_metrics(self):
        g = pc.Gauge('job_last_success_unixtime',
                     'Last time Consul8s succeeded',
                     registry=self._registry)
        g.set_to_current_time()
        if self._location is not None:
            pc.push_to_gateway(self._location,
                               job='consul8s',
                               registry=self._registry)

        self._registry = pc.CollectorRegistry()
