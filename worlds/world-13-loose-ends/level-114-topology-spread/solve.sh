#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl label node "$(cq_node_name node01)" topology.kubernetes.io/zone=zone-a --overwrite >/dev/null
kubectl label node "$(cq_node_name node02)" topology.kubernetes.io/zone=zone-b --overwrite >/dev/null
kubectl patch deploy api -n spread-lab --type merge -p '{"spec":{"template":{"spec":{"topologySpreadConstraints":[{"maxSkew":1,"topologyKey":"topology.kubernetes.io/zone","whenUnsatisfiable":"DoNotSchedule","labelSelector":{"matchLabels":{"app":"api"}},"matchLabelKeys":["pod-template-hash"]}]}}}}' >/dev/null
kubectl rollout status deploy/api -n spread-lab --timeout=120s >/dev/null
gone() { [ "$(kubectl get pods -n spread-lab -l app=api --no-headers | wc -l)" = 4 ]; }
cq_wait 90 gone
