#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl create secret generic db-creds -n config-lab --from-literal=username=app --from-literal='password=S3cure!'
kubectl create configmap app-settings -n config-lab --from-literal=LOG_LEVEL=debug --from-literal=REGION=eu-central
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: app
  namespace: config-lab
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ["sleep", "3600"]
    envFrom:
    - configMapRef: {name: app-settings}
    volumeMounts:
    - name: creds
      mountPath: /etc/creds
      readOnly: true
  volumes:
  - name: creds
    secret:
      secretName: db-creds
      defaultMode: 0400
EOF
kubectl wait --for=condition=Ready pod/app -n config-lab --timeout=60s
