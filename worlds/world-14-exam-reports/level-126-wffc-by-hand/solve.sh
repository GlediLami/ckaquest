#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-wffc
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: wffc-pv
spec:
  capacity:
    storage: 200Mi
  accessModes: ["ReadWriteOnce"]
  storageClassName: local-wffc
  local:
    path: /mnt/wffc
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values: ["$(cq_node_name node02)"]
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: wffc-pvc
  namespace: wffc-lab
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: local-wffc
  resources:
    requests:
      storage: 200Mi
---
apiVersion: v1
kind: Pod
metadata:
  name: wffc-pod
  namespace: wffc-lab
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ["sleep", "3600"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: wffc-pvc
EOF
kubectl wait --for=condition=Ready pod/wffc-pod -n wffc-lab --timeout=120s
