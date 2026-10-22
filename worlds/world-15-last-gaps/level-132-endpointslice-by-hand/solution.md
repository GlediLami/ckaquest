# Solution

```yaml
apiVersion: v1
kind: Service
metadata:
  name: legacy
  namespace: ext-lab
spec:
  ports:
  - name: http
    port: 80
---
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: legacy-1
  namespace: ext-lab
  labels:
    kubernetes.io/service-name: legacy
addressType: IPv4
ports:
- name: http
  port: 5678
endpoints:
- addresses: ["<pod IP>"]
```

```bash
k get pod legacy-backend -n legacy-host -o wide
k apply -f legacy.yaml
k run t -n ext-lab --rm -it --image=curlimages/curl:8.11.1 --restart=Never -- curl -s http://legacy.ext-lab
```
