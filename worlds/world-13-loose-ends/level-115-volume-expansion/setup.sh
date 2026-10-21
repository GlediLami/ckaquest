#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl delete sc slow-local --ignore-not-found >/dev/null 2>&1
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: slow-local
provisioner: rancher.io/local-path
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data
  namespace: grow-lab
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: slow-local
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: db
  namespace: grow-lab
spec:
  containers:
  - name: db
    image: busybox:1.36
    command: ["sh", "-c", "echo rows > /data/table; sleep 3600"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: data
EOF
kubectl wait --for=condition=Ready pod/db -n grow-lab --timeout=120s >/dev/null 2>&1 || true
kubectl create configmap original -n grow-lab \
  --from-literal=pvc="$(kubectl get pvc data -n grow-lab -o jsonpath='{.metadata.uid}')" \
  --from-literal=pod="$(kubectl get pod db -n grow-lab -o jsonpath='{.metadata.uid}')" >/dev/null
