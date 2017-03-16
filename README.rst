Consul8s
========

Consul8s is a tool (currently in development) that retrieves services from
Consul and creates Kubernetes Services. This allows a pod deployed in
Kubernetes to request a single DNS/ClusterIP record and load balance across the
service endpoints listed in Kubernetes.


Syncing a Service
-----------------

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
    name: consul-1
    registration: consul
  annotations:
    consul8s/service.name: foo
spec:
  ports:
    - name: http
      port: 80
      nodePort: 31310

```

It is important to omit the `selector` for the Kubernetes Service. Without the
`selector`, Kubernetes will rely on a separate configuration for endpoints
(provided in this case with Consul8s).

Consul8s will periodically poll the Kubernetes API to find services which use
Consul registration, query Consul for endpoints, then configure the Kubernetes
Service Endpoints.
