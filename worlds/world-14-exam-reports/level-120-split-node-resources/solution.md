# Solution

```bash
k describe node node01 | grep -A7 -E 'Allocatable|Allocated resources'
# say: allocatable cpu 16, memory 9000Mi. Others request 950m and 290Mi.
# free: 15050m, 8710Mi. Per pod with ~10% headroom: about 4500m, 2600Mi.
k scale deploy wordpress -n resource-lab --replicas=0
k set resources deploy wordpress -n resource-lab -c init-db  --requests=cpu=4500m,memory=2600Mi
k set resources deploy wordpress -n resource-lab -c wordpress --requests=cpu=4500m,memory=2600Mi
k scale deploy wordpress -n resource-lab --replicas=3
k get pods -n resource-lab -o wide
```
