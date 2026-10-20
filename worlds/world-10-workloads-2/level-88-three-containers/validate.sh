#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
ready3() { [ "$(jp trio-lab pod/trio '{.status.containerStatuses[*].ready}')" = "true true true" ]; }
node_env() { [ "$(kubectl exec trio -n trio-lab -c info -- printenv MY_NODE 2>/dev/null)" = "$(jp trio-lab pod/trio '{.spec.nodeName}')" ]; }
check "trio has containers writer, reader, info" out_eq "writer reader info" kubectl get pod trio -n trio-lab -o jsonpath='{.spec.containers[*].name}'
check 2 "all 3 containers are ready" ready3
check 2 "reader sees what writer writes" out_match "[0-9]{2}:[0-9]{2}" kubectl logs trio -n trio-lab -c reader --tail=1
check 2 "info has MY_NODE = its node name" node_env
finish
