# Solution

```bash
k create secret tls app-tls -n tls-ingress \
  --cert=~/ckaquest-work/127/tls.crt --key=~/ckaquest-work/127/tls.key
k create ingress app-ingress -n tls-ingress --class=nginx \
  --rule="secure.example.com/*=app:80,tls=app-tls"
k get ingress app-ingress -n tls-ingress -o yaml
```
