# 🎓 Mission Debrief: Deployment Update Stuck

## What Happened

Your deployment tried to roll out a new version with image `nginx:nonexistent-v2.0-xyz` that doesn't exist in Docker Hub. The deployment got stuck with some pods on the old working version and some failing to start with the new broken version.

Kubernetes' RollingUpdate strategy protected you from total downtime by keeping old pods running while new ones failed.

## How Kubernetes Behaved

**RollingUpdate Strategy** (default for Deployments):

```
1. Create new ReplicaSet with new pod template
2. Scale up new ReplicaSet (create new pods)
3. Wait for new pods to be Ready
4. Scale down old ReplicaSet (terminate old pods)
5. Repeat until all replicas updated
```

Your deployment got stuck at **step 3**—new pods never became Ready because the image didn't exist. Kubernetes kept retrying but also kept your old pods running, preventing total service outage!

**Deployment states**:
- **Progressing**: Update is happening
- **Complete**: All replicas updated and healthy  
- **Failed**: Update couldn't complete (stuck here!)

## The Correct Mental Model

**How Deployments manage ReplicaSets**:

```
Deployment: web-app
├── ReplicaSet-abc123 (old version, replicas: 3)
│   ├── Pod-1 (Running) ✅
│   ├── Pod-2 (Running) ✅
│   └── Pod-3 (Running) ✅
└── ReplicaSet-xyz789 (new version, replicas: 0 → trying to become 3)
    ├── Pod-4 (ImagePullBackOff) ❌
    ├── Pod-5 (ImagePullBackOff) ❌
    └── Pod-6 (Not created yet)
```

**RollingUpdate parameters**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # Max extra pods during update (1 = 4 total pods max)
    maxUnavailable: 0  # Max unavailable pods (0 = always keep 3 running)
```

**Rollback mechanism**:
- Kubernetes keeps old ReplicaSets (scaled to 0)
- `kubectl rollout undo` just swaps which ReplicaSet is scaled up
- Near-instant recovery (pods already exist, just scaled)

## Real-World Incident Example

**Company**: E-commerce platform during Black Friday  
**Impact**: 2-hour partial outage, 30% of users affected  
**Cost**: $1.2M in lost sales + $200K in SLA penalties  

**What happened**:
A developer tagged and pushed image `checkout-service:v2.3.1` to the CI/CD pipeline, which started deploying. But they forgot to push that tag to Docker Hub—only the commit was pushed, not the tag.

The deployment started rolling out during peak Black Friday traffic (4PM EST). Half the pods updated to the broken version and entered ImagePullBackOff. Half stayed on v2.3.0 (working).

Users experienced:
- 50% of checkout requests failed (hit broken pods)
- Intermittent cart errors
- Payment processing timeouts

**Why it took 2 hours to fix**:
1. Team didn't know about `kubectl rollout undo` (new to K8s)
2. Tried to "fix forward" by building new image (30 min CI/CD time)
3. New build also failed (wrong tag again)
4. Tried manual pod deletion (didn't help—deployment kept creating broken ones)
5. Finally, senior engineer suggested checking rollout history
6. Ran `kubectl rollout undo deployment/checkout-service`
7. **Instant recovery in 30 seconds**

**The lesson**: One command could have saved $1.4M and 2 hours of chaos.

## Commands You Mastered

```bash
# Check deployment status
kubectl get deployment <name> -n <namespace>
kubectl describe deployment <name> -n <namespace>

# Check rollout status (shows if stuck/progressing/complete)
kubectl rollout status deployment/<name> -n <namespace>

# View rollout history
kubectl rollout history deployment/<name> -n <namespace>

# View specific revision details
kubectl rollout history deployment/<name> --revision=2 -n <namespace>

# Rollback to previous version (MOST IMPORTANT!)
kubectl rollout undo deployment/<name> -n <namespace>

# Rollback to specific revision
kubectl rollout undo deployment/<name> --to-revision=3 -n <namespace>

# Pause a rollout (stop updates mid-rollout)
kubectl rollout pause deployment/<name> -n <namespace>

# Resume a paused rollout
kubectl rollout resume deployment/<name> -n <namespace>

# Restart deployment (rolling restart with same image)
kubectl rollout restart deployment/<name> -n <namespace>

# See all ReplicaSets (old ones are kept for rollback!)
kubectl get replicasets -n <namespace>
```

## Understanding Deployment Annotations

The `kubernetes.io/change-cause` annotation helps track why changes were made:

```yaml
metadata:
  annotations:
    kubernetes.io/change-cause: "Update to v2.0 for new features"
```

Shows up in `kubectl rollout history`:
```
REVISION  CHANGE-CAUSE
1         Initial deployment v1.0
2         Update to v2.0 (broken)
```

**Best practice**: Always set this annotation when updating deployments!

## Prevention Strategies

1. **Image existence validation**:
   ```bash
   # Before deploying, verify image exists
   docker pull nginx:v2.0  # Will fail if doesn't exist
   ```

2. **CI/CD pipeline checks**:
   - Verify image is pushed to registry
   - Run smoke tests before deploying
   - Use image digests instead of tags for immutability

3. **Progressive rollout**:
   ```yaml
   spec:
     replicas: 100
     strategy:
       rollingUpdate:
         maxUnavailable: 10%  # Only 10 pods at a time
   ```

4. **Deployment readiness gates**:
   - Use readiness probes to prevent bad pods from receiving traffic
   - Set `minReadySeconds` to ensure pods are stable before continuing

5. **Automated rollback**:
   - Monitor deployment health
   - Auto-rollback if error rate spikes
   - Tools: Flagger, Argo Rollouts

6. **Canary deployments**:
   - Update 10% of pods first
   - Monitor metrics
   - Continue if healthy, rollback if not

## What's Next?

You've learned the most critical production skill: **how to rollback a failed deployment**.

Next level: You'll learn about ReplicaSets and how Deployments use them under the hood!

**Pro tip**: In production, always keep rollout history. The default is 10 revisions. You can change with:
```yaml
spec:
  revisionHistoryLimit: 10  # Keep last 10 ReplicaSets
```
