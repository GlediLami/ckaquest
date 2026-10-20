# 🎓 Mission Debrief: Canary Weight Imbalance

## What Happened

Your canary deployment had a 50/50 traffic split (5 stable pods, 5 canary pods) instead of the intended 90/10 split.

This means half your users were exposed to the new, untested canary version - defeating the entire purpose of canary deployments!

Canary deployments should expose only a small percentage of users to the new version for safe testing.

## How Kubernetes Behaved

**Service load balancing** (Kubernetes default):

```
Service selector: app=myapp (matches both stable and canary)
    ↓
Endpoints: All pods with app=myapp label
    ↓
Load balancer distributes evenly across ALL endpoints
    ↓
With 5 stable + 5 canary = 10 total pods
Each pod gets ~10% of traffic
    ↓
stable pods: 5 × 10% = 50% traffic ❌
canary pods: 5 × 10% = 50% traffic ❌
```

**Broken configuration**:

```
Stable (v1): 5 pods  ──┐
                        ├──▶ Service ──▶ 50% v1, 50% v2 ❌
Canary (v2): 5 pods  ──┘

Result: Half your users are guinea pigs!
```

**Fixed configuration**:

```
Stable (v1): 9 pods  ──┐
                        ├──▶ Service ──▶ 90% v1, 10% v2 ✅
Canary (v2): 1 pod   ──┘

Result: Only 10% of users test new version
```

## The Correct Mental Model

### Canary Deployment Strategy

**Concept**: Gradually roll out new version to a small subset of users, monitor for issues, then progressively increase traffic.

```
┌─────────────────────────────────────────────┐
│         PHASE 1: Stable Only                 │
│  ┌──────────────┐                            │
│  │   Service    │───────▶┌──────────────┐   │
│  │ (selector:   │        │ Stable Pods  │   │
│  │  app=myapp)  │        │ (v1.0)       │   │
│  └──────────────┘        │ 10 replicas  │   │
│                          └──────────────┘   │
│                                              │
│  All users → v1.0                            │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│    PHASE 2: Canary Introduction (10%)        │
│  ┌──────────────┐        ┌──────────────┐   │
│  │   Service    │────┬──▶│ Stable Pods  │   │
│  │ (selector:   │    │   │ (v1.0)       │   │
│  │  app=myapp)  │    │   │ 9 replicas   │   │
│  └──────────────┘    │   └──────────────┘   │
│                      │                       │
│                      │   ┌──────────────┐   │
│                      └──▶│ Canary Pods  │   │
│                          │ (v2.0)       │   │
│                          │ 1 replica    │   │
│                          └──────────────┘   │
│                                              │
│  90% users → v1.0                             │
│  10% users → v2.0 (testing)                   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│    PHASE 3: Increase Canary (50%)            │
│  ┌──────────────┐        ┌──────────────┐   │
│  │   Service    │────┬──▶│ Stable Pods  │   │
│  │              │    │   │ (v1.0)       │   │
│  │              │    │   │ 5 replicas   │   │
│  └──────────────┘    │   └──────────────┘   │
│                      │                       │
│                      │   ┌──────────────┐   │
│                      └──▶│ Canary Pods  │   │
│                          │ (v2.0)       │   │
│                          │ 5 replicas   │   │
│                          └──────────────┘   │
│                                              │
│  50% users → v1.0                             │
│  50% users → v2.0                             │
│  (No errors? Increase more!)                 │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│    PHASE 4: Full Canary (100%)               │
│  ┌──────────────┐        ┌──────────────┐   │
│  │   Service    │────┬─X─│ Stable Pods  │   │
│  │              │    │   │ (v1.0)       │   │
│  │              │    │   │ 0 replicas   │   │
│  └──────────────┘    │   └──────────────┘   │
│                      │                       │
│                      │   ┌──────────────┐   │
│                      └──▶│ Canary Pods  │   │
│                          │ (v2.0)       │   │
│                          │ 10 replicas  │   │
│                          └──────────────┘   │
│                                              │
│  100% users → v2.0 ✅                          │
│  Delete old stable deployment                │
└─────────────────────────────────────────────┘
```

### Traffic Split Calculation

**Formula**:

```
Canary traffic % = (Canary pods / Total pods) × 100
```

**Examples**:

| Stable Pods | Canary Pods | Total | Canary % | Use Case |
|-------------|-------------|-------|----------|----------|
| 9 | 1 | 10 | 10% | Initial canary |
| 8 | 2 | 10 | 20% | Expand testing |
| 5 | 5 | 10 | 50% | Half and half |
| 2 | 8 | 10 | 80% | Nearly full |
| 0 | 10 | 10 | 100% | Complete rollout |
| 95 | 5 | 100 | 5% | Large-scale 5% canary |

**Common canary percentages**:

```
10% canary: 9 stable, 1 canary
20% canary: 4 stable, 1 canary
25% canary: 3 stable, 1 canary
50% canary: 1 stable, 1 canary
```

### Canary vs Other Strategies

| Strategy | Traffic Split | Resource Usage | Rollback Speed | Risk Level |
|----------|---------------|----------------|----------------|------------|
| **Canary** | Gradual (10→50→100%) | 1-2x (during transition) | Fast (scale down) | Low (limited exposure) |
| **Blue-Green** | Instant (0→100%) | 2x (both versions) | Instant (switch selector) | Medium (all at once) |
| **Rolling** | Gradual (pod by pod) | 1x + surge | Medium (rollback) | Medium (gradual) |
| **Recreate** | Instant (downtime) | 1x | Slow (redeploy) | High (no testing) |

## Real-World Incident Example

**Company**: E-learning platform (2M students)  
**Impact**: 8-hour performance degradation affecting 1M students  
**Cost**: $1.2M in refunds + massive support load  

**What happened**:

The team developed a new version (v2.5) with a "performance optimization" - they changed the database query pattern. They planned a canary rollout to test it safely.

**Intended plan**: 10% canary (test with 200K students)

**Actual configuration**:

```yaml
# Intended configuration (but NOT what was deployed)
# stable: 90 replicas
# canary: 10 replicas

# Actual deployed configuration:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable
spec:
  replicas: 50  # ❌ WRONG
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
spec:
  replicas: 50  # ❌ WRONG - should be ~5 for 10%
```

Someone misread the config and deployed 50/50 instead of 90/10!

**The cascade** (Monday, 8 AM - peak hours):

```
08:00 - Deploy canary (v2.5)
08:00 - Intended: 10% of traffic to canary
08:00 - Actual: 50% of traffic to canary (50/50 split) ❌
08:05 - 1M students (50%) now using v2.5
08:10 - Dashboard shows "error rate normal" (because they monitor v1 and v2 separately)
08:15 - Support tickets start flooding in:
        "Assignments loading slowly"
        "Videos won't load"
        "Getting timeout errors"
08:20 - Check metrics: v2.5 has 10x higher latency than v1
08:20 - Realize: "Optimization" broke performance!
08:25 - Decision: Rollback canary
08:26 - Scale canary to 0: kubectl scale deployment app-canary --replicas=0
08:28 - All traffic back to v1
08:30 - Performance returns to normal
08:30 - But damage done: 1M students affected for 30 minutes
        During prime homework submission time!
```

**Why it was catastrophic**:
- **Peak hours** - 8 AM, students doing homework before school
- **50% exposure** - Should have been 10%, instead 1M students affected
- **Misleading metrics** - Monitoring didn't aggregate or highlight the split
- **Performance regression** - The "optimization" actually made things worse
- **Support overload** - 5,000 tickets in 30 minutes

**What should have happened**:

```
With correct 10% canary:
08:00 - Deploy canary (10% traffic)
08:05 - 200K students on v2.5 (not 1M)
08:10 - Notice latency issue
08:15 - Scale canary to 0
08:16 - Only 200K affected, 1.8M never saw the issue
08:20 - Fix identified and patched
```

**Root cause analysis**:

1. **Human error** in configuration:
```yaml
# Developer meant to write:
stable: 90
canary: 10

# But wrote:
stable: 50  # Copy-paste error
canary: 50
```

2. **No validation** of traffic split:
```bash
# Should have checked:
TOTAL=$(kubectl get pods -l app=myapp -n prod | grep Running | wc -l)
CANARY=$(kubectl get pods -l track=canary -n prod | grep Running | wc -l)
PCT=$((CANARY * 100 / TOTAL))
if [ $PCT -gt 15 ]; then
    echo "ERROR: Canary is $PCT%, expected ~10%"
    exit 1
fi
```

3. **Insufficient monitoring** - No alert for "canary traffic > 15%"

**The fix implemented**:

1. **Automated traffic validation**:
```bash
#!/bin/bash
# canary-deploy.sh

STABLE_REPLICAS=$1
CANARY_REPLICAS=$2
TARGET_PCT=$3

ACTUAL_PCT=$((CANARY_REPLICAS * 100 / (STABLE_REPLICAS + CANARY_REPLICAS)))

if [ $ACTUAL_PCT -gt $((TARGET_PCT + 5)) ]; then
    echo "ERROR: Canary will be $ACTUAL_PCT%, target is $TARGET_PCT%"
    exit 1
fi

kubectl scale deployment app-stable --replicas=$STABLE_REPLICAS
kubectl scale deployment app-canary --replicas=$CANARY_REPLICAS
```

2. **Pre-deployment checks**:
```yaml
# CI/CD pipeline validation
- name: Validate canary split
  run: |
    python3 validate_canary.py \
      --stable $(yq '.spec.replicas' stable.yaml) \
      --canary $(yq '.spec.replicas' canary.yaml) \
      --max-canary-pct 15
```

3. **Real-time monitoring**:
```
# Prometheus alert
- alert: CanaryTrafficTooHigh
  expr: (sum(kube_pod_status_ready{deployment="app-canary"}) / sum(kube_pod_status_ready{app="myapp"})) > 0.15
  for: 2m
  annotations:
    summary: "Canary deployment has > 15% of traffic"
```

**Lessons learned**:
1. **Validate traffic splits** before deploying
2. **Automate canary percentage calculations** - don't rely on mental math
3. **Monitor actual traffic distribution** - alert if canary gets too much
4. **Start very small** - 5% or even 1% for risky changes
5. **Have rollback automation** - instant scale to 0

## Commands You Mastered

```bash
# Scale deployments for canary
kubectl scale deployment app-stable --replicas=9 -n <namespace>
kubectl scale deployment app-canary --replicas=1 -n <namespace>

# Check replica counts
kubectl get deployments -n <namespace>

# Calculate actual traffic split
STABLE=$(kubectl get deployment app-stable -n <namespace> -o jsonpath='{.status.readyReplicas}')
CANARY=$(kubectl get deployment app-canary -n <namespace> -o jsonpath='{.status.readyReplicas}')
TOTAL=$((STABLE + CANARY))
CANARY_PCT=$((CANARY * 100 / TOTAL))
echo "Canary traffic: $CANARY_PCT%"

# Check service endpoints (see all pods)
kubectl get endpoints app-service -n <namespace>

# Test traffic distribution (sampling)
for i in {1..100}; do
  kubectl run -it --rm test-$i --image=busybox --restart=Never -n <namespace> -- wget -q -O- app-service
done | grep -c "Canary"

# Quick rollback (scale canary to 0)
kubectl scale deployment app-canary --replicas=0 -n <namespace>

# Progressive rollout (increase canary)
kubectl scale deployment app-canary --replicas=2 -n <namespace>  # 20%
# Monitor...
kubectl scale deployment app-canary --replicas=5 -n <namespace>  # 50%
# Monitor...
kubectl scale deployment app-canary --replicas=10 -n <namespace> # 100%
kubectl scale deployment app-stable --replicas=0 -n <namespace>  # Remove old
```

## Best Practices for Canary Deployments

### ✅ DO:

1. **Start small** (5-10% canary):
   ```bash
   # For 10% canary with 10 total pods:
   kubectl scale deployment app-stable --replicas=9
   kubectl scale deployment app-canary --replicas=1
   ```

2. **Validate traffic split**:
   ```bash
   # Calculate before deploying
   CANARY_PCT=$((CANARY_REPLICAS * 100 / (STABLE_REPLICAS + CANARY_REPLICAS)))
   echo "Canary will get $CANARY_PCT% of traffic"
   ```

3. **Monitor canary metrics separately**:
   ```
   # Prometheus queries
   http_requests_total{version="stable"}
   http_requests_total{version="canary"}
   
   # Compare error rates
   rate(http_errors_total{version="canary"}[5m])
   rate(http_errors_total{version="stable"}[5m])
   ```

4. **Use gradual rollout**:
   ```
   10% → monitor 30min → 25% → monitor 1hr → 50% → monitor 2hr → 100%
   ```

5. **Have automatic rollback**:
   ```yaml
   # Flagger (progressive delivery tool)
   apiVersion: flagger.app/v1beta1
   kind: Canary
   spec:
     analysis:
       threshold: 10
       maxWeight: 50
       stepWeight: 10
   ```

### ❌ DON'T:

1. **Don't start with 50/50 split**:
   ```bash
   # Bad: Too much exposure
   stable: 5, canary: 5  # 50% canary
   
   # Good: Limited exposure
   stable: 9, canary: 1  # 10% canary
   ```

2. **Don't ignore canary metrics**:
   ```
   # Bad: Only monitor overall metrics
   # Good: Compare stable vs canary separately
   ```

3. **Don't rush through stages**:
   ```
   # Bad: 10% → 100% in 5 minutes
   # Good: 10% → 30min → 25% → 1hr → 50% → 2hr → 100%
   ```

4. **Don't forget rollback plan**:
   ```bash
   # Always have this ready:
   kubectl scale deployment app-canary --replicas=0
   ```

## Canary Deployment Patterns

### Pattern 1: Progressive Rollout

```bash
#!/bin/bash
# progressive-canary.sh

TOTAL_PODS=10
STAGES=(1 2 5 10)  # 10%, 20%, 50%, 100%

for CANARY in "${STAGES[@]}"; do
    STABLE=$((TOTAL_PODS - CANARY))
    CANARY_PCT=$((CANARY * 100 / TOTAL_PODS))
    
    echo "Deploying canary at $CANARY_PCT% ($CANARY pods)"
    kubectl scale deployment app-stable --replicas=$STABLE
    kubectl scale deployment app-canary --replicas=$CANARY
    
    echo "Monitoring for 5 minutes..."
    sleep 300
    
    # Check error rate
    ERROR_RATE=$(check_canary_errors)
    if [ $ERROR_RATE -gt 1 ]; then
        echo "ERROR RATE TOO HIGH! Rolling back..."
        kubectl scale deployment app-canary --replicas=0
        kubectl scale deployment app-stable --replicas=$TOTAL_PODS
        exit 1
    fi
done

echo "Canary successful! Cleaning up stable..."
kubectl delete deployment app-stable
```

### Pattern 2: A/B Testing Canary

```yaml
# Use different selectors for A and B testing
apiVersion: v1
kind: Service
metadata:
  name: app-variant-a
spec:
  selector:
    app: myapp
    variant: a  # User segment A
---
apiVersion: v1
kind: Service
metadata:
  name: app-variant-b
spec:
  selector:
    app: myapp
    variant: b  # User segment B (canary)
```

### Pattern 3: Geographic Canary

```yaml
# Deploy canary to specific region first
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary-us-west
spec:
  template:
    spec:
      nodeSelector:
        region: us-west
      # Canary version
---
# Stable in all other regions
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable-global
spec:
  # Stable version everywhere else
```

## What's Next?

You've learned how to configure canary deployments with proper traffic splits for safe testing.

Next level: StatefulSet vs Deployment! You'll learn why using Deployments for stateful applications can cause data loss.

**Key takeaway**: Canary deployments must have correct replica ratios to limit user exposure. Always validate your traffic split before deploying!
