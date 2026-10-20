#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl delete pod app -n sidecar-lab --now
cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: app
  namespace: sidecar-lab
spec:
  initContainers:
  - name: log-shipper
    image: busybox:1.36
    restartPolicy: Always
    command: ["sh", "-c", "touch /var/log/app/app.log; tail -F /var/log/app/app.log"]
    volumeMounts:
    - name: logs
      mountPath: /var/log/app
  containers:
  - name: app
    image: busybox:1.36
    command: ["sh", "-c", "mkdir -p /var/log/app; while true; do echo \"$(date) order processed\" >> /var/log/app/app.log; sleep 2; done"]
    volumeMounts:
    - name: logs
      mountPath: /var/log/app
  volumes:
  - name: logs
    emptyDir: {}
EOF
kubectl wait --for=condition=Ready pod/app -n sidecar-lab --timeout=90s; sleep 6
