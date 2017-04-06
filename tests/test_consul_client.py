import uuid
import unittest

import click
import mock
import requests
import requests.exceptions

from consul8s import consul_client


class TestGettingActiveEndpointForService(unittest.TestCase):

    def setUp(self):
        self.http = mock.Mock(requests)
        self.base_url = str(mock.Mock(str()))
        self.output = mock.Mock(click)

        self.cc = consul_client.ConsulClient(self.http, self.base_url, self.output)

    def test_service_with_no_endpoints(self):
        self.http.get.return_value.json.return_value = []
        service = 'foo'
        url = self.base_url + '/v1/catalog/service/' + service + "?passing"

        returned = self.cc.get_active_endpoints_for_service(service)

        self.http.get.assert_called_once_with(url, timeout=60)

        self.assertEqual([([], None)], returned)

    def test_service_with_a_single_endpoint(self):
        instance = self._consul_service_instance()
        self.http.get.return_value.json.return_value = [instance]
        service = 'foo'
        url = self.base_url + '/v1/catalog/service/' + service + "?passing"

        returned = self.cc.get_active_endpoints_for_service(service)

        self.http.get.assert_called_once_with(url, timeout=60)

        self.assertEqual([([instance['Address']], instance['ServicePort'])], returned)

    def test_service_with_multiple_endpoints(self):
        instance_1 = self._consul_service_instance('10.0.0.1')
        instance_2 = self._consul_service_instance('10.0.0.2')
        self.http.get.return_value.json.return_value = [instance_1, instance_2]
        service = 'foo'
        url = self.base_url + '/v1/catalog/service/' + service + "?passing"

        returned = self.cc.get_active_endpoints_for_service(service)

        self.http.get.assert_called_once_with(url, timeout=60)

        self.assertEqual([([instance_1['Address'],
                           instance_2['Address']], instance_2['ServicePort'])],
                         returned)

    def test_service_timeout_to_consul(self):
        self.http.get.side_effect = requests.exceptions.Timeout('test')

        service = 'foo'
        self.assertRaisesRegexp(consul_client.ConsulClientRequestException,
                                'test',
                                self.cc.get_active_endpoints_for_service,
                                service)

    def test_service_http_error(self):
        self.http.get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError('test')

        service = 'foo'
        self.assertRaisesRegexp(consul_client.ConsulClientRequestException,
                                'test',
                                self.cc.get_active_endpoints_for_service,
                                service)

    def _consul_service_instance(self, address='127.0.0.1', service_port=5000):
        'Create a minimum needed consul service instance'
        return {
           'ID': str(uuid.uuid4()),
           'Address': address,
           'ServicePort': service_port,
        }
