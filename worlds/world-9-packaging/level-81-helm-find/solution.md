# Solution

```bash
helm list -A
helm list -A | grep webapp-1.0.0
helm uninstall old-api -n helm-team-a
helm uninstall old-web -n helm-team-b
```
