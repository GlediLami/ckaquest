#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
IP="$(kubectl get pod legacy-backend -n legacy-host -o jsonpath='{.status.podIP}')"
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: legacy
  namespace: ext-lab
spec:
  ports:
  - name: http
    port: 80
    protocol: TCP
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
  protocol: TCP
endpoints:
- addresses: ["$IP"]
EOF
sleep 5
