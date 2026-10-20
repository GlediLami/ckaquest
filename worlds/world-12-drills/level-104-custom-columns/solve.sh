#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
sleep 5
kubectl get pods -n drill-104 --sort-by=.metadata.name -o custom-columns=POD:.metadata.name,IMAGE:.spec.containers[0].image,NODE:.spec.nodeName > "$CQ_WORK/104/pods.txt"
