import requests.exceptions


class ConsulClientRequestException(Exception):
    "Exception while making a request to Consul"

class ConsulClient(object):

    def __init__(self, http, consul_url, output):
        self._http = http
        self._base_url = consul_url
        self._output = output

    def get_active_endpoints_for_service(self, service):
        url = self._url_for_service(service)
        try:
            resp = self._http.get(url, timeout=60)
        except requests.exceptions.Timeout as e:
            self._output('Timeout connecting to Consul')
            raise ConsulClientRequestException(e)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self._output('HTTP Error {0}'.format(str(e)))
            raise ConsulClientRequestException(e)

        addresses = []
        port = None
        for service in resp.json():
            addresses.append(service['Address'])
            port = service['ServicePort']

        return (addresses, port)

    def _url_for_service(self, service):
        return '{0}/v1/catalog/service/{1}'.format(self._base_url, service)
