
def create_endpoint_doc(service, endpoints, port):
    ips = [{'ip': ip} for ip in endpoints]
    service_ports = service.obj['spec']['ports']
    ports = ports_from_service_ports(service_ports, port)

    doc = {
      "kind": "Endpoints",
      "apiVersion": "v1",
      "metadata": {
          "name": service.name,
          "namespace": service.namespace,
          "labels": {
              "name": service.name
          },
      },
      "subsets": [
          {
              "addresses": ips,
              "ports": ports
          }
      ]
    }
    return doc

def ports_from_service_ports(service_ports, port):
    # Right now only support 1 port per service :(
    service_port = service_ports[0]
    port_def = {"port": port}
    if 'name' in service_port:
        port_def['name'] = service_port['name']
    return [port_def]
