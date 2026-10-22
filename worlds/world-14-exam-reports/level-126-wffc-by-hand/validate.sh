#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
N2="$(cq_node_name node02)"
check "StorageClass local-wffc: no-provisioner, WaitForFirstConsumer" out_eq "kubernetes.io/no-provisioner WaitForFirstConsumer" kubectl get sc local-wffc -o jsonpath='{.provisioner} {.volumeBindingMode}'
check "PV wffc-pv: 200Mi, ReadWriteOnce, local-wffc, local /mnt/wffc" out_eq "200Mi ReadWriteOnce local-wffc /mnt/wffc" kubectl get pv wffc-pv -o jsonpath='{.spec.capacity.storage} {.spec.accessModes[0]} {.spec.storageClassName} {.spec.local.path}'
check "PV wffc-pv only on node02" field_eq - pv/wffc-pv '{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}' "$N2"
check 2 "PVC wffc-pvc is Bound to wffc-pv" out_eq "Bound wffc-pv" kubectl get pvc wffc-pvc -n wffc-lab -o jsonpath='{.status.phase} {.spec.volumeName}'
check 2 "wffc-pod runs on node02 with /data mounted" out_eq "Running $N2 wffc-pvc" kubectl get pod wffc-pod -n wffc-lab -o jsonpath='{.status.phase} {.spec.nodeName} {.spec.volumes[0].persistentVolumeClaim.claimName}'
finish
