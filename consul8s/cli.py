import os
import random
import time

import click
import pykube

from consul8s import kube_generation
from consul8s import prometheus_metrics


@click.command()
@click.option('--kube-config-path', '-k', default=os.getenv('KUBECONFIG'), help='Path to your Kube Config')
@click.option('--namespace', '-n', default='default', help='namespace to search')
@click.option('--interval', '-i', default='60', help='Interval between loops')
@click.option('--run-once', '-1', is_flag=True, help='Run once instead of looping forever')
@click.option('--prometheus', '-p', is_flag=True, help='Enable Prometheus metrics')
def main(kube_config_path, namespace, interval, run_once, prometheus):
    """Consul integration with Kubernetes"""
    if kube_config_path:
        config = pykube.KubeConfig.from_file(kube_config_path)
    else:
        config = pykube.KubeConfig.from_service_account()
    api = pykube.HTTPClient(config)

    metrics = prometheus_metrics.PrometheusMetrics(prometheus)

    if run_once:
        with metrics.eval_timer.time():
            evaluate(api, namespace)
    else:
        while True:
            with metrics.eval_timer.time():
                evaluate(api, namespace)
            time.sleep(int(interval))


def evaluate(api, namespace):
    services = pykube.Service.objects(api).filter(namespace=namespace,
                                                  selector={'consul8s_source': 'consul'})
    click.echo('Found {0} services'.format(len(services)))
    for service in services:
        click.echo('Service: {0}'.format(service.name))
        click.echo('Getting endpoints')
        (endpoints, port) = get_consul_endpoints_for_service(None, None, service)
        click.echo('Found endpoints {0}'.format(endpoints))
        doc = kube_generation.create_endpoint_doc(service, endpoints, port)
        click.echo('Creating endpoint {0}'.format(doc))
        try:
            pykube.Endpoint(api, doc).update()
            click.echo('Updated endpoints')
        except pykube.exceptions.HTTPError:
            pykube.Endpoint(api, doc).create()
            click.echo('Created endpoints')


def get_consul_endpoints_for_service(HTTP, host, service):
    # Fake this for now until we can test against a consul setup
    endpoints = [
        '10.0.0.1',
        '10.6.1.1',
        '10.5.2.1',
        '10.4.3.1',
        '10.3.4.1',
        '10.2.5.1',
        '10.1.6.1',
    ]
    return (random.sample(endpoints, 3), 9376)


