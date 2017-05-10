import os
import random
import socket
import time

import click
import pykube
import requests

from consul8s import consul_client
from consul8s import kube_generation
from consul8s import prometheus_metrics


@click.command()
@click.option('--kube-config-path', '-k', default=os.getenv('KUBECONFIG'), help='Path to your Kube Config')
@click.option('--namespace', '-n', default='default', help='namespace to search')
@click.option('--interval', '-i', default='60', help='Interval between loops')
@click.option('--run-once', '-1', is_flag=True, help='Run once instead of looping forever')
@click.option('--prometheus', '-p', is_flag=True, help='Enable Prometheus metrics')
@click.option('--consul', '-c', default='localhost:8500', help='Hostname:Port of Consul')
def main(kube_config_path, namespace, interval, run_once, prometheus, consul):
    """Consul integration with Kubernetes"""
    if kube_config_path:
        config = pykube.KubeConfig.from_file(kube_config_path)
    else:
        config = pykube.KubeConfig.from_service_account()
    api = pykube.HTTPClient(config)

    metrics = prometheus_metrics.PrometheusMetrics(prometheus)
    consul_url = 'http://{0}'.format(consul)
    cclient = consul_client.ConsulClient(requests, consul_url, click.echo)

    if run_once:
        with metrics.eval_timer.time():
            evaluate_for_endpoints(api, namespace, metrics, cclient)
            evaluate_for_registration(api, namespace, metrics, cclient)
    else:
        while True:
            with metrics.eval_timer.time():
                evaluate_for_endpoints(api, namespace, metrics, cclient)
                evaluate_for_registration(api, namespace, metrics, cclient)
            time.sleep(int(interval))


def evaluate_for_endpoints(api, namespace, metrics, consul):
    """Updated Kube services with endpoints from consul"""
    services = pykube.Service.objects(api).filter(namespace=namespace,
                                                  selector={'consul8s_source': 'consul'})
    number_of_services = len(services)
    metrics.number_of_consul_sourced_services.set(number_of_services)
    click.echo('Found {0} services needing kube endpoints'.format(number_of_services))
    for service in services:
        click.echo('Service: {0}'.format(service.name))
        click.echo('Getting endpoints')
        consul_service_name = service.obj['metadata']['annotations']['consul8s/service.name']
        endpoints = consul.get_active_endpoints_for_service(consul_service_name)
        click.echo('Found endpoints {0}'.format(endpoints))
        ip_endpoints = list(filter_for_ips(endpoints))
        click.echo('IP endpoints {0}'.format(ip_endpoints))
        doc = kube_generation.create_endpoint_doc(service, ip_endpoints)
        click.echo('Creating endpoint {0}'.format(doc))
        try:
            pykube.Endpoint(api, doc).update()
            click.echo('Updated endpoints')
        except pykube.exceptions.HTTPError:
            pykube.Endpoint(api, doc).create()
            click.echo('Created endpoints')

def evaluate_for_registration(api, namespace, metrics, consul):
    """Registers kube ELBs into Consul as a service"""
    services = pykube.Service.objects(api).filter(namespace=namespace,
                                                  selector={'consul8s_source': 'kubernetes'})
    number_of_services = len(services)
    metrics.number_of_kubernetes_sourced_services.set(number_of_services)
    click.echo('Found {0} services for consul registration'.format(number_of_services))
    for service in services:
        click.echo('Service: {0}'.format(service.name))
        remove_service = service.obj['metadata']['annotations'].get('consul8s/service.remove_registration', 'false').lower() == 'true'
        if remove_service:
            click.echo('Ensuring it doesn\'t exist in Consul')
            consul.ensure_kube_service_deregistered(service.obj)
        else:
            click.echo('Ensuring it exists in Consul')
            consul.ensure_kube_service_registered(service.obj)


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
    return [(random.sample(endpoints, 3), 9376),
            (random.sample(endpoints, 2), 9378)]


def filter_for_ips(items):
    """Generator that yields endpoints of only IPv4 addrs from endpoints

    This can be used to remove non-IPv4 addresses from the (addrs, port)
    tuples used for endpoints.
    """
    for (addresses, port) in items:
        ips = []
        for addr in addresses:
            try:
                socket.inet_aton(addr)
            except socket.error:
                pass
            else:
                ips.append(addr)
        yield (ips, port)
