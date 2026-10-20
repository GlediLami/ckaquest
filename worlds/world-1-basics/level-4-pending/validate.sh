#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check "hungry-app still has a CPU request" field_ne ckaquest pod/hungry-app "{.spec.containers[0].resources.requests.cpu}" ""
check "hungry-app still has a memory request" field_ne ckaquest pod/hungry-app "{.spec.containers[0].resources.requests.memory}" ""
check "hungry-app was scheduled to a node" field_ne ckaquest pod/hungry-app "{.spec.nodeName}" ""
check 2 "hungry-app is Ready" pod_ready ckaquest hungry-app
finish
