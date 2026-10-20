#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
N="static-web-$(cq_node_name node01)"
check "a manifest for static-web is in node01's staticPodPath" node_ok node01 'grep -rl "name: static-web" "$(awk "/staticPodPath/ {print \$2}" /var/lib/kubelet/config.yaml)"'
check 2 "mirror pod $N is Ready" pod_ready static-lab "$N"
check "it runs nginx:1.27-alpine" field_eq static-lab "pod/$N" '{.spec.containers[0].image}' nginx:1.27-alpine
check "it has label app=static-web" field_eq static-lab "pod/$N" '{.metadata.labels.app}' static-web
finish
