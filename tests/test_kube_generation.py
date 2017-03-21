import random
import unittest

import mock

from consul8s import kube_generation


class TestCreateEndpointDoc(unittest.TestCase):

    def setUp(self):
        self.service = mock.MagicMock()
        self.port = random.choice(range(1024, 2048))

        self.fut = kube_generation.create_endpoint_doc

    def test_endpoints_are_addresses(self):
        endpoints = [mock.Mock(), mock.Mock]
        addresses = [{'ip': ip} for ip in endpoints]

        doc = self.fut(self.service, endpoints, self.port)

        self.assertEqual(addresses, doc['subsets'][0]['addresses'])

    def test_ports_from_endpoints(self):
        self.service.obj = self._service_obj()
        endpoints = [mock.Mock(), mock.Mock]
        addresses = [{'ip': ip} for ip in endpoints]

        doc = self.fut(self.service, endpoints, self.port)

        self.assertEqual(self.port, doc['subsets'][0]['ports'][0]['port'])
        self.assertEqual('http', doc['subsets'][0]['ports'][0]['name'])

    def test_unnamed_port(self):
        self.service.obj = self._service_obj(ports=[{'port': 81}])
        endpoints = [mock.Mock(), mock.Mock]
        addresses = [{'ip': ip} for ip in endpoints]

        doc = self.fut(self.service, endpoints, self.port)

        self.assertEqual(self.port, doc['subsets'][0]['ports'][0]['port'])
        self.assertNotIn('name', doc['subsets'][0]['ports'][0])

    def test_multiple_named_ports(self):
        ports = [
            {'name': 'foo2',
            'port': 82},
            {'name': 'foo3',
            'port': 83}]
        self.service.obj = self._service_obj(ports=ports)
        endpoints = [mock.Mock(), mock.Mock]
        addresses = [{'ip': ip} for ip in endpoints]

        doc = self.fut(self.service, endpoints, self.port)

        self.assertEqual(self.port, doc['subsets'][0]['ports'][0]['port'])
        self.assertEqual('foo2', doc['subsets'][0]['ports'][0]['name'])
        self.assertEqual('foo3', doc['subsets'][0]['ports'][1]['name'])


    def _service_obj(self, ports=None):
        if ports is None:
            ports =  [{'name': 'http',
                       'port': 80}]
        obj = {
            'spec': {
                'ports': ports
        }}
        return obj
