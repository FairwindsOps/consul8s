


class ConsulClient(object):

    def __init__(self, http, consul_url):
        self._http = http
        self._base_url = consul_url

    def get_active_endpoints_for_service(self, service):
        url = self._url_for_service(service)
        results = self._http.get(url, timeout=60)
        return results.json()

    def _url_for_service(self, service):
        return '{0}/v1/catalog/service/{1}'.format(self._base_url, service)
