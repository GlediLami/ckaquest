# 🎓 Mission Debrief: Pending Pod Problem

## What Happened

Your pod was stuck in `Pending` status because it requested 999 CPUs and 999Gi of memory—far more than any node in your cluster can provide. The Kubernetes scheduler couldn't find a node with enough resources, so the pod never started.

## How Kubernetes Behaved

The **Kubernetes scheduler** is responsible for placing pods on nodes. Here's the process:

1. **Pod created**: API server accepts your pod manifest
2. **Scheduler watches**: Sees new unscheduled pod
3. **Filtering**: Eliminates nodes that don't meet requirements (resources, taints, affinity)
4. **Scoring**: Ranks remaining nodes by best fit
5. **Binding**: Assigns pod to winning node

Your pod failed at step 3—**no nodes passed the filter** because none had 999 CPUs available.

## The Correct Mental Model

**Resource Requests vs Limits**:

- **Requests**: Guaranteed minimum resources (used for scheduling)
- **Limits**: Maximum resources allowed (enforced at runtime)

```yaml
resources:
  requests:      # "I need at least this much"
    memory: "64Mi"
    cpu: "100m"
  limits:        # "Don't let me use more than this"
    memory: "128Mi"
    cpu: "200m"
```

**CPU units**:
- `1` = 1 full CPU core
- `100m` = 0.1 CPU (100 millicores)
- `1000m` = 1 CPU

**Memory units**:
- `Mi` = Mebibytes (1024²)
- `Gi` = Gibibytes (1024³)
- `M` = Megabytes (1000²)
- `G` = Gigabytes (1000³)

**What happens when a node is full**:
```
Node capacity: 4 CPUs, 8Gi memory
Already allocated: 3 CPUs, 6Gi memory
Available: 1 CPU, 2Gi memory

Pod requests 2 CPUs → ❌ Can't schedule (insufficient CPU)
Pod requests 500m CPU, 1Gi memory → ✅ Can schedule
```

## Real-World Incident Example

**Company**: SaaS startup (100K users)  
**Impact**: 6-hour deployment freeze, missed product deadline  
**Cost**: Lost enterprise customer worth $500K ARR

**What happened**:
A developer copy-pasted pod configuration from a "production-grade" blog post that set requests to `cpu: 2` and `memory: 4Gi` for every microservice. Their dev cluster had small nodes (2 CPUs each).

When they deployed 10 microservices, only the first 1-2 pods scheduled. The rest stayed Pending.

**Why it took 6 hours**:
- Developers thought it was a cluster issue, contacted ops
- Ops thought nodes were unhealthy, started debugging infrastructure
- No one checked `kubectl describe pod` events for 5 hours
- Finally discovered via: `kubectl get events --sort-by='.lastTimestamp'`

**The fix**: Changed requests to `cpu: 100m, memory: 128Mi` based on actual usage. All pods scheduled immediately.

**Lesson**: 
1. Start with small resource requests (50-100m CPU, 64-128Mi memory)
2. Monitor actual usage with `kubectl top pod`
3. Adjust based on real data, not guesses

## Commands You Mastered

```bash
# Check pod status
kubectl get pod <name> -n <namespace>

# See why pod isn't scheduling (Events are key!)
kubectl describe pod <name> -n <namespace>

# Check resource requests/limits
kubectl get pod <name> -n <namespace> -o yaml | grep -A 6 resources:

# See node capacity and allocatable resources
kubectl describe nodes

# Check actual resource usage (requires metrics-server)
kubectl top pod <name> -n <namespace>
kubectl top nodes

# See all cluster events sorted by time
kubectl get events --sort-by='.lastTimestamp' -n <namespace>
```

## Prevention Strategies

1. **Set reasonable defaults**: Use LimitRanges to prevent unrealistic requests
2. **Monitor utilization**: Deploy metrics-server and track actual usage
3. **Use VPA** (Vertical Pod Autoscaler): Automatically adjust requests based on usage
4. **Cluster autoscaling**: Add nodes automatically when pods are pending
5. **Admission webhooks**: Validate resource requests before accepting pods
6. **Resource quotas**: Prevent one team from consuming entire cluster

## Understanding Scheduling Failures

Common reasons pods stay Pending:

| Reason | Event Message | Solution |
|--------|---------------|----------|
| Insufficient CPU | `Insufficient cpu` | Reduce CPU requests or add nodes |
| Insufficient Memory | `Insufficient memory` | Reduce memory requests or add nodes |
| No nodes match selector | `node(s) didn't match node selector` | Fix nodeSelector labels |
| Taints prevent scheduling | `node(s) had taint that pod didn't tolerate` | Add tolerations or remove taints |
| Volume not available | `persistentvolumeclaim not found` | Create PVC first |

## What's Next?

You've mastered three pod states:
- ✅ CrashLoopBackOff (bad container command)
- ✅ ImagePullBackOff (bad image reference)
- ✅ Pending (resource constraints)

Next up: Learn how labels and selectors connect services to pods!
