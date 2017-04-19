"""Metrics client using Prometheus Push Gateway"""
import prometheus_client as pc


class PrometheusMetrics(object):

    def __init__(self, run):
        if run:
            pc.start_http_server(8000)

        self.eval_timer = pc.Summary('loop_time_seconds', 'Time to evaluate services')
        self.number_of_consul_sourced_services = pc.Gauge(
            'number_of_consul_sourced_services',
            'Number of services in Kubernetes that rely on endpoint data from Consul')

        self.number_of_kubernetes_sourced_services = pc.Gauge(
            'number_of_kubernetes_sourced_services',
            'Number of services in Kubernetes that are synced to Consul')
