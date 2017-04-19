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

        return [(addresses, port)]

    def ensure_kube_service_registered(self, service_manifest):
        """Registers/updates a Kube service registration into Consul

        - service_manifest: manifest of a Kubernetes service
        """
        doc = self._doc_from_manifest(service_manifest, self._consul_registration_doc)
        self._output(doc)
        url = self._url_for_catalog_registration()
        self._put(url, doc)

    def ensure_kube_service_deregistered(self, service_manifest):
        """Deregisters a Kube service registration from Consul

        - service_manifest: manifest of a Kubernetes service
        """
        doc = self._doc_from_manifest(service_manifest, self._consul_deregistration_doc)
        self._output(doc)
        url = self._url_for_catalog_deregistration()
        self._put(url, doc)

    def _port_number_from_name(self, ports, name):
        for port in ports:
            if port['name'] == name:
                return port['port']
        raise Exception('No port with name {0}'.format(name))

    def _put(self, url, data):
        try:
            resp = self._http.put(url, timeout=60, json=data)
        except requests.exceptions.Timeout as e:
            self._output('Timeout connecting to Consul')
            raise ConsulClientRequestException(e)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self._output('HTTP Error {0}'.format(str(e)))
            raise ConsulClientRequestException(e)

    def _doc_from_manifest(self, service_manifest, func):
        """Creates a doc from a Kube manifest.

        `service_manifest` has properties extracted then applied to `func`. The
        result of `func` is returned.
        """
        service_metadata = service_manifest['metadata']
        service_spec = service_manifest['spec']

        endpoint = service_metadata['annotations']['domainName']
        consul_name = service_metadata['annotations']['consul8s/service.name']
        service_id = service_metadata['annotations'].get('consul8s/service.id', consul_name)
        port_name = service_metadata['annotations']['consul8s/service.port_name']

        port_number = self._port_number_from_name(service_spec['ports'], port_name)

        doc = func(consul_name, service_id, endpoint, port_number)
        return doc

    def _consul_registration_doc(self, service, service_id, address, port):
        doc = {
            'Node': 'Kubernetes',
            'Address': address,
            'Service': {
                'ID': service_id,
                'Service': service,
                'Address': address,
                'Port': port,
            },
        }
        return doc

    def _consul_deregistration_doc(self, service, service_id, address, port):
        doc = {
            'Node': 'Kubernetes',
            'ServiceID': service_id,
        }
        return doc

    def _url_for_service(self, service):
        return '{0}/v1/catalog/service/{1}?passing'.format(self._base_url, service)

    def _url_for_catalog_registration(self):
        return '{0}/v1/catalog/register'.format(self._base_url)

    def _url_for_catalog_deregistration(self):
        return '{0}/v1/catalog/deregister'.format(self._base_url)
