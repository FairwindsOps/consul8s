import unittest

import mock
import requests

from consul8s import consul_client


class TestGettingActiveEndpointForService(unittest.TestCase):

    def setUp(self):
        self.http = mock.Mock(requests)
        self.base_url = str(mock.Mock(str()))

        self.cc = consul_client.ConsulClient(self.http, self.base_url)

    def test_service_with_no_endpoints(self):
        self.http.get.return_value.json.return_value = []
        service = 'foo'
        url = self.base_url + '/v1/catalog/service/' + service

        returned = self.cc.get_active_endpoints_for_service(service)

        self.http.get.assert_called_once_with(url, timeout=60)

        self.assertEqual([], returned)
