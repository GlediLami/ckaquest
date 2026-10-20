# Solution

```bash
k describe httproute blog-route -n blog     # no parent status, or ResolvedRefs False
k get gateway,svc -n blog
k edit httproute blog-route -n blog
#   parentRefs: - name: web-gw
#   backendRefs: - name: blog, port: 80
```
