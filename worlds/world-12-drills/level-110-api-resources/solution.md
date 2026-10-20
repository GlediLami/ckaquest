# Solution

```bash
k api-resources | grep -E 'poddisruptionbudgets|ingressclasses|^persistentvolumes'
printf 'pdb\nnetworking.k8s.io\nfalse\n' > ~/ckaquest-work/110/answers.txt
```
