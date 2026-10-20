# Solution

```bash
k create secret generic db-creds -n config-lab --from-literal=username=app --from-literal='password=S3cure!'
k create cm app-settings -n config-lab --from-literal=LOG_LEVEL=debug --from-literal=REGION=eu-central
k run app -n config-lab --image=busybox:1.36 $do -- sleep 3600 > app.yaml
```

```yaml
    envFrom:
    - configMapRef: {name: app-settings}
    volumeMounts:
    - {name: creds, mountPath: /etc/creds, readOnly: true}
  volumes:
  - name: creds
    secret: {secretName: db-creds, defaultMode: 0400}
```
