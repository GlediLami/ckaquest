# Solution

```bash
k create deploy shop -n drill-107 --image=nginx:1.27-alpine --replicas=2 $do > ~/ckaquest-work/107/deploy.yaml
vim ~/ckaquest-work/107/deploy.yaml
```

```yaml
      containers:
      - image: nginx:1.27-alpine
        name: nginx
        env:
        - {name: MODE, value: prod}
        resources:
          requests: {cpu: 50m, memory: 32Mi}
        readinessProbe:
          httpGet: {path: /, port: 80}
```
