
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
    ports = []
    for service_port in service_ports:
        port_def = {"port": port}
        if 'name' in service_port:
            port_def['name'] = service_port['name']
        ports.append(port_def)
    return ports
