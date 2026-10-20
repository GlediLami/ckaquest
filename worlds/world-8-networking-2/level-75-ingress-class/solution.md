# Solution

```bash
k get ingressclass
k edit ingress docs-ingress -n ingress-lab     # spec.ingressClassName: nginx
k get ingress -n ingress-lab                   # ADDRESS appears after a few seconds
```
