#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
affinity() { jp node-affinity pod/gpu-workload '{.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0]}'; }
check "node01 still carries accelerator=gpu (label not moved or removed)" field_eq - node/ckaquest-worker '{.metadata.labels.accelerator}' gpu
check 2 "required node affinity uses key accelerator, value gpu" out_match '"key":"accelerator".*"values":\["gpu"\]' affinity
check 2 "gpu-workload is Running" pod_running node-affinity gpu-workload
check "gpu-workload runs on the GPU node (ckaquest-worker)" field_eq node-affinity pod/gpu-workload '{.spec.nodeName}' ckaquest-worker
finish
