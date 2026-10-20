#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "kube-proxy uses /var/lib/kube-proxy/config.conf" field_eq kube-system ds/kube-proxy '{.spec.template.spec.containers[0].command[1]}' --config=/var/lib/kube-proxy/config.conf
check 2 "kube-proxy is ready on all 3 nodes" field_eq kube-system ds/kube-proxy '{.status.numberReady}' 3
check 2 "http://echo.proxy-lab answers from a pod" in_cluster_ok proxy-lab busybox:1.36 wget -q -T 5 -O /dev/null http://echo.proxy-lab
finish
