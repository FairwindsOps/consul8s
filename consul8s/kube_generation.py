
def create_endpoint_doc(service, endpoints):
    service_ports = service.obj['spec']['ports']
    subsets_doc = create_subsets_doc(service_ports, endpoints)

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
      "subsets": subsets_doc,
    }
    return doc

def create_subsets_doc(service_ports, endpoints):
    """Creates the subsets needed for Kube services

    Expcects the ports from a kube service manifest
    and a list of endpoints:
        [ ([ip1, ip2], port), ([ip3, ip4], port) ]
    """
    subsets = []
    for ips, port in endpoints:
        print port
        addresses = [{'ip': ip} for ip in ips]
        ports = ports_from_service_ports(service_ports, port)
        subsets.append({
            "addresses": addresses,
            "ports": ports
        })
    return subsets

def ports_from_service_ports(service_ports, port):
    # Right now only support 1 port per service :(
    ports = []
    for service_port in service_ports:
        port_def = {"port": port}
        if 'name' in service_port:
            port_def['name'] = service_port['name']
        ports.append(port_def)
    return ports
