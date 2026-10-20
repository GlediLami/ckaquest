# Solution

```bash
k create secret tls secure-tls -n secure-shop --cert=~/ckaquest-work/74/tls.crt --key=~/ckaquest-work/74/tls.key
k edit gateway web-gw -n secure-shop
```

```yaml
  listeners:
  - name: http
    protocol: HTTP
    port: 80
  - name: https
    protocol: HTTPS
    port: 443
    hostname: secure.example.com
    tls:
      mode: Terminate
      certificateRefs:
      - name: secure-tls
```

```bash
k edit httproute secure-route -n secure-shop
#   parentRefs:
#   - name: web-gw
#     sectionName: http
#   - name: web-gw
#     sectionName: https
```
