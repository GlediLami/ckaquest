#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl scale deploy cache -n anti-lab --replicas=0 >/dev/null
kubectl patch deploy cache -n anti-lab --type merge -p '{"spec":{"replicas":3,"template":{"spec":{"affinity":{"podAntiAffinity":{"requiredDuringSchedulingIgnoredDuringExecution":[{"labelSelector":{"matchLabels":{"app":"cache"}},"topologyKey":"kubernetes.io/hostname"}]}}}}}}' >/dev/null
settled() { [ "$(kubectl get deploy cache -n anti-lab -o jsonpath='{.status.readyReplicas}/{.status.updatedReplicas}')" = 2/3 ] \
  && [ "$(kubectl get pods -n anti-lab -l app=cache --no-headers | wc -l)" = 3 ]; }
cq_wait 120 settled
