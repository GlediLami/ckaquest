# Solution

```bash
k get pods -n np-pick --show-labels
cat ~/ckaquest-work/130/policy-*.yaml
# 1: every pod in every namespace         too open
# 2: frontend, but all ports               too open
# 3: frontend, TCP 8080                    right
# 4: everyone                              too open
# 5: label app=front matches nothing       frontend blocked
k apply -f ~/ckaquest-work/130/policy-3.yaml
k exec frontend -n np-pick -- wget -qO- -T 3 http://backend:8080
```
