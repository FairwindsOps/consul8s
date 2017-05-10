Consul8s
========

[![Docker Repository on Quay](https://quay.io/repository/reactiveops/consul8s/status "Docker Repository on Quay")](https://quay.io/repository/reactiveops/consul8s)

Consul8s is a tool (currently in development) that retrieves services from
Consul and creates Kubernetes Services. This allows a pod deployed in
Kubernetes to request a single DNS/ClusterIP record and load balance across the
service endpoints listed in Kubernetes.


Creating Kubernetes Service Endpoints Based on Consul
-----------------------------------------------------

To sync a Consul service requires a Kubernetes Service with specific labels and
annotations. This metadata instructs Consul8s how to create the specific record.

A label `registration: consul` is required for Consul8s to find appropriate
Kubernetes services.

An annotation of `consul8s/service.name` is used to find the matching service
in Consul.


Example Kubernetes Service configuration:

```
---
apiVersion: v1
kind: Service
metadata:
  name: svc-foo
  labels:
    name: foo
    consul8s_source: consul
  annotations:
    consul8s/service.name: foo
spec:
  ports:
    - name: http
      port: 80

```

It is important to omit the `selector` for the Kubernetes Service. Without the
`selector`, Kubernetes will rely on a separate configuration for endpoints
(provided in this case with Consul8s).

Consul8s will periodically poll the Kubernetes API to find services which use
Consul registration, query Consul for endpoints, then configure the Kubernetes
Service Endpoints.

Changing Port Specs
^^^^^^^^^^^^^^^^^^^

Changing the port spec for a service can lead to periods of missing endpoints.
This is due to the time between a service is changed and Consul8s updating the
endpoints.

A way to do this without downtime would be to add a new port with a new name,
migrate applications over, then remove the old port. This isn't ideal though.


Creating Consul Service Based on Kubernetes Services
----------------------------------------------------

It is possible to register Kubernetes services into consul. This will rely on a
DNS record created out-of-band or via the
[route53-kubernetes](https://github.com/wearemolecule/route53-kubernetes)
mapping service.

Label:
* `consul8s_source` must be set to `kubernetes` .

Annotations:
* `consul8s/service.name` is the name of the service in Consul.
* `consul8s/service.id` The Consul ServiceID. Defaults to the `consul8s/service.name` if not specified.
* `consul8s/service.port_name` is the port name in this manifest to register in Consul. The port number will be looked up via this name.
* `consul8s/service.tags` a comma-separated string of tags to apply to the service
* `domainName` is the name being registered into Consul.

Removing the Kubernetes service *will not* remove the Consul registration.

Removing the Consul service can be done with an annotation of `consul8s/service.remove_registration: true`. This will remove the registration in Consul to allow the service to drain.

Only IPv4 addresses will sync to Kubernetes. Kubernetes will only accept IP addresses. DNS records will not be resolved into an address when syncing.


```
---
apiVersion: v1
kind: Service
metadata:
  name: svc-foo
  labels:
    name: foo
    consul8s_source: kubernetes
    dns: route53
  annotations:
    consul8s/service.name: foo
    consul8s/service.port_name: http
    consul8s/service.id: foo_00
    consul8s/service.remove_registration: "false"
    consul8s/service.tags "foo,bar"
    domainName: foo.example.com
spec:
  ports:
    - name: http
      port: 80

```

Installation
------------

    pip install consul

Usage
-----

To use it:

    $ consul8s --help

Monitoring
----------

Consul8s tries to fail quickly and exit in the event of errors, relying on
Kubernetes to restart the process. Simple monitoring can be that Consul8s has
not restarted recently and has run for a multiple of the `--interval`. This is
helpful although may not be sufficient (in the event that the Consul8s process
hangs).

Metrics can be used to ensure that Consul8s is actually processing properly.

Metrics
^^^^^^^

Metric collection can be enabled via the `--prometheus` option for hosting metrics at port `8000`.

The `loop_time_seconds` metric can be used to monitor that Consul8s has
evaluated Kubernetes services in a timely manner.

A derivative of `loop_time_seconds_count` will let you know that this has succeeded recently.

An alert similar to "`loop_time_seconds_count` > N" may also be useful.
