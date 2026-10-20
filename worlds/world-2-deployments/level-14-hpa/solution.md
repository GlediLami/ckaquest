# Solution

The container has no CPU request. The HPA computes utilization as usage divided by request, so it cannot compute anything.

```bash
k describe hpa web-backend-hpa -n ckaquest     # FailedGetResourceMetric: missing request for cpu
k set resources deploy web-backend -n ckaquest --requests=cpu=100m
k get hpa -n ckaquest -w                       # after about a minute: 0%/50%
```

You can also edit the Deployment and add under the container:

```yaml
resources:
  requests:
    cpu: 100m
```
