# Solution

The username in the Secret was encoded twice. It decodes to `YWRtaW4=` instead of `admin`. The `=` fails the format check in the app.

```bash
k get secret db-credentials -n secret-encoding -o jsonpath='{.data.username}' | base64 -d    # YWRtaW4=
k create secret generic db-credentials -n secret-encoding \
  --from-literal=username=admin --from-literal=password=secretpass123 \
  --dry-run=client -o yaml | k apply -f -
k get pod database-client -n secret-encoding -o yaml | k replace --force -f -
k logs database-client -n secret-encoding
```

Another way: edit the Secret with `stringData`, which takes plain text and lets the API server encode it.
