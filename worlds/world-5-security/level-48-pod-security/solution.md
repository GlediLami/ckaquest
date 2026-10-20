```bash
kubectl apply -f ~/ckaquest-work/48/secure-app.yaml
# Error: violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false, ...
vim ~/ckaquest-work/48/secure-app.yaml
```
```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: busybox:1.36
    command: ["sh", "-c", "echo running as $(id -u); sleep 86400"]
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
```
```bash
kubectl apply -f ~/ckaquest-work/48/secure-app.yaml
kubectl -n pss-lab get pod secure-app
```
