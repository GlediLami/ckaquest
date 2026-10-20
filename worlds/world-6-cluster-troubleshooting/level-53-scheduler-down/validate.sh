#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "kube-scheduler pod is Ready" pod_ready kube-system kube-scheduler-ckaquest-control-plane
check "scheduler manifest runs the kube-scheduler binary" node_ok controlplane 'grep -qE "^ *- kube-scheduler$" /etc/kubernetes/manifests/kube-scheduler.yaml'
check 2 "deployment web has 2 ready pods" deploy_ready sched-lab web 2
finish
