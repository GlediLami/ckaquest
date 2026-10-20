#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
tainted() { jp - "node/$1" '{.spec.taints[?(@.key=="dedicated")].effect}' | grep -q NoSchedule; }
toleration() { jp taints-tolerations pod/regular-app '{.spec.tolerations[?(@.key=="dedicated")]}'; }
check "node01 keeps its dedicated taint" tainted ckaquest-worker
check "node02 keeps its dedicated taint" tainted ckaquest-worker2
check 2 "regular-app tolerates dedicated=gpu:NoSchedule" out_match '"effect":"NoSchedule".*"value":"gpu"|"value":"gpu".*"effect":"NoSchedule"' toleration
check 2 "regular-app is Running" pod_running taints-tolerations regular-app
finish
