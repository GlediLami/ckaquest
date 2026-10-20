apiVersion: v1
kind: Pod
metadata:
  name: resource-hungry-app
  namespace: resourcequota
spec:
  containers:
  - name: app
    image: nginx:latest
    resources:
      requests:
        cpu: "2500m"
        memory: "1Gi"
      limits:
        cpu: "3"
        memory: "2Gi"
