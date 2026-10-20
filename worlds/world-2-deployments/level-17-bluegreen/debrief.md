# 🎓 Mission Debrief: Blue-Green Deployment Gone Wrong

## What Happened

You deployed a new version of your application (GREEN) using a blue-green deployment strategy, but users were still seeing the old version (BLUE).

The root cause: **The service selector wasn't updated to point to the new deployment**.

Both deployments were running, but the service was only routing traffic to the blue (old) pods because of the label selector mismatch.

## How Kubernetes Behaved

**Service selector matching**:

```
Service selector:
  app: myapp
  version: blue

app-blue pods (OLD):
  labels:
    app: myapp ✅
    version: blue ✅
  Result: MATCH → Gets traffic ✅

app-green pods (NEW):
  labels:
    app: myapp ✅
    version: green ❌ (doesn't match "blue")
  Result: NO MATCH → No traffic ❌
```

**Service endpoints**:

```
Before fix:
kubectl get endpoints app-service
NAME          ENDPOINTS
app-service   10.1.0.5:8080,10.1.0.6:8080,10.1.0.7:8080
              ↑ These are the BLUE pods

After fix (selector changed to version: green):
kubectl get endpoints app-service
NAME          ENDPOINTS
app-service   10.1.0.8:8080,10.1.0.9:8080,10.1.0.10:8080
              ↑ These are the GREEN pods
```

## The Correct Mental Model

### Blue-Green Deployment Strategy

**Concept**: Run two identical production environments (Blue and Green), switch traffic instantly by updating service selector.

```
┌─────────────────────────────────────────────┐
│         STEP 1: Initial State               │
│  ┌──────────────┐        ┌──────────────┐   │
│  │   Service    │───────▶│  Blue Pods   │   │
│  │ (selector:   │        │ (v1.0)       │   │
│  │ version=blue)│        │ 3 replicas   │   │
│  └──────────────┘        └──────────────┘   │
│                                              │
│  Users → Service → Blue (v1.0)               │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│    STEP 2: Deploy Green (new version)       │
│  ┌──────────────┐        ┌──────────────┐   │
│  │   Service    │───────▶│  Blue Pods   │   │
│  │ (selector:   │        │ (v1.0)       │   │
│  │ version=blue)│        │ 3 replicas   │   │
│  └──────────────┘        └──────────────┘   │
│                                              │
│                          ┌──────────────┐   │
│                          │  Green Pods  │   │
│                          │ (v2.0)       │   │
│                          │ 3 replicas   │   │
│                          └──────────────┘   │
│                          ↑ Running but       │
│                            no traffic yet    │
│                                              │
│  Users → Service → Blue (v1.0)               │
│  Green (v2.0) running, ready for testing     │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│    STEP 3: Test Green (internal traffic)    │
│  ┌──────────────┐        ┌──────────────┐   │
│  │   Service    │───────▶│  Blue Pods   │   │
│  │ (selector:   │        │ (v1.0)       │   │
│  │ version=blue)│        │ 3 replicas   │   │
│  └──────────────┘        └──────────────┘   │
│                                              │
│  ┌──────────────┐        ┌──────────────┐   │
│  │Test Service  │───────▶│  Green Pods  │   │
│  │ (selector:   │        │ (v2.0)       │   │
│  │ version=green)        │ 3 replicas   │   │
│  └──────────────┘        └──────────────┘   │
│                                              │
│  Users → Service → Blue (v1.0)               │
│  QA/Team → Test Service → Green (v2.0)       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  STEP 4: Switch! (Update selector)           │
│  ┌──────────────┐        ┌──────────────┐   │
│  │   Service    │    X   │  Blue Pods   │   │
│  │ (selector:   │        │ (v1.0)       │   │
│  │ version=GREEN)        │ 3 replicas   │   │
│  └─────┬────────┘        └──────────────┘   │
│        │                                     │
│        │                 ┌──────────────┐   │
│        └────────────────▶│  Green Pods  │   │
│                          │ (v2.0)       │   │
│                          │ 3 replicas   │   │
│                          └──────────────┘   │
│                                              │
│  Users → Service → Green (v2.0) ✅            │
│  INSTANT CUTOVER (update selector)           │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  STEP 5: Cleanup (or keep for rollback)     │
│  ┌──────────────┐                           │
│  │   Service    │───────▶┌──────────────┐   │
│  │ (selector:   │        │  Green Pods  │   │
│  │ version=green)        │ (v2.0)       │   │
│  └──────────────┘        │ 3 replicas   │   │
│                          └──────────────┘   │
│                                              │
│  Option A: Delete blue deployment            │
│  Option B: Keep blue for instant rollback    │
│                                              │
│  Users → Service → Green (v2.0)               │
└─────────────────────────────────────────────┘
```

### Blue-Green vs Rolling Update

| Aspect | Blue-Green | Rolling Update |
|--------|------------|----------------|
| **Resource usage** | 2x (both versions running) | 1x + surge |
| **Switchover** | Instant (change selector) | Gradual (pod by pod) |
| **Testing** | Test full prod environment | Limited testing window |
| **Rollback** | Instant (revert selector) | Slower (re-deploy) |
| **Risk** | Lower (tested before switch) | Medium (gradual exposure) |
| **Cost** | Higher (double resources) | Lower |

### Service Selector Mechanics

```yaml
# Service
apiVersion: v1
kind: Service
spec:
  selector:
    app: myapp      # Must match
    version: blue   # AND must match
    
# Pods must have BOTH labels to receive traffic
```

**Label matching rules**:

```yaml
# Pod with app=myapp, version=blue
labels:
  app: myapp
  version: blue
# Matches service? YES ✅

# Pod with app=myapp, version=green  
labels:
  app: myapp
  version: green
# Matches service? NO ❌ (version doesn't match)

# Pod with app=myapp (no version label)
labels:
  app: myapp
# Matches service? NO ❌ (version label missing)
```

## Real-World Incident Example

**Company**: Video streaming platform (5M concurrent users)  
**Impact**: 45-minute delay in critical bug fix rollout, continued service degradation  
**Cost**: $850K in CDN overages + customer refunds  

**What happened**:

A critical bug was discovered in production (v1.5): video player was requesting full video files instead of using HLS streaming, causing 100x bandwidth usage.

The team quickly fixed the bug and deployed v1.6 using blue-green strategy:

```yaml
# Deployed green deployment with fix
apiVersion: apps/v1
kind: Deployment
metadata:
  name: player-green
spec:
  replicas: 50
  template:
    metadata:
      labels:
        app: player
        version: green
    spec:
      containers:
      - name: player
        image: player:v1.6  # Fixed version
```

They tested green internally - the fix worked! But they forgot one crucial step: **switching the main service selector**.

**The cascade** (Friday evening, peak hours):

```
18:00 - Bug discovered (massive bandwidth spike)
18:15 - Fix developed (v1.6)
18:30 - Deploy green deployment (v1.6)
18:35 - Test green deployment via test service - works! ✅
18:40 - Announce "fix deployed" to team
18:45 - Wait for CDN costs to drop...
18:50 - CDN costs still skyrocketing 📈
18:55 - Check metrics: Users still on v1.5!
19:00 - Panic: "Why are users on old version??"
19:05 - Check service selector:

kubectl get service player-service -o yaml
spec:
  selector:
    app: player
    version: blue  # ❌ STILL POINTING TO OLD VERSION!

19:10 - Realize the mistake
19:12 - Update selector to version: green
19:13 - Traffic switches instantly
19:15 - CDN bandwidth drops to normal
19:30 - Incident resolved
```

**Why it was catastrophic**:
- **Peak hours** - Friday evening, maximum concurrent users
- **Bandwidth costs** - $850K in overage charges in just 90 minutes
- **User experience** - Slow video loading, buffering
- **Cascading effect** - Impacted CDN, origin servers
- **Human error** - Forgot crucial step in deployment process

**What users experienced**:

```
18:00 - Videos loading slowly (bug)
18:40 - Team announces "fix deployed"
18:40-19:13 - Still experiencing slow loading
            - Complaining on social media
            - "They said it's fixed but it's not!"
19:13 - Suddenly videos load fast again ✅
```

**The fix implemented**:

1. **Automated switchover script**:
```bash
#!/bin/bash
# blue-green-deploy.sh

GREEN_VERSION=$1
SERVICE_NAME="player-service"

echo "Deploying green version: $GREEN_VERSION"

# 1. Deploy green
kubectl apply -f green-deployment.yaml

# 2. Wait for green to be ready
kubectl wait --for=condition=available --timeout=300s deployment/player-green

# 3. Run smoke tests
./test-green.sh || exit 1

# 4. Switch service selector
kubectl patch service $SERVICE_NAME -p '{"spec":{"selector":{"version":"green"}}}'

echo "✅ Traffic switched to green"
echo "Blue deployment still running for rollback"
echo "Run './cleanup-blue.sh' after validation period"
```

2. **Validation checklist**:
```
Blue-Green Deployment Checklist:
☐ 1. Deploy green deployment
☐ 2. Verify green pods are running (3/3 ready)
☐ 3. Test green deployment (internal service)
☐ 4. Run smoke tests
☐ 5. **UPDATE SERVICE SELECTOR** ← Don't forget!
☐ 6. Verify traffic switched (check endpoints)
☐ 7. Monitor metrics for 15 minutes
☐ 8. Keep blue running for 1 hour (quick rollback)
☐ 9. Delete blue deployment after validation
```

3. **Monitoring dashboard**:
```
Blue-Green Deployment Status:
- Blue pods: 50/50 ready
- Green pods: 50/50 ready
- Service selector: version=blue ⚠️
  ↑ ALERT IF MISMATCH DETECTED
- Traffic to blue: 100%
- Traffic to green: 0%
```

**Lessons learned**:
1. **Automate the switchover** - Don't rely on manual steps
2. **Verify traffic routing** - Check endpoints, not just pod status
3. **Monitor the full flow** - From service → endpoints → pods
4. **Use checklists** - Critical steps shouldn't be forgotten
5. **Test the switchover** - In staging, practice the full process

## Commands You Mastered

```bash
# Check service selector
kubectl get service <name> -n <namespace> -o yaml | grep -A 5 selector

# Check which pods match the service
kubectl get endpoints <service-name> -n <namespace>

# Patch service selector (atomic update)
kubectl patch service <name> -n <namespace> -p '{"spec":{"selector":{"version":"green"}}}'

# Edit service (manual)
kubectl edit service <name> -n <namespace>

# Test which version is serving traffic
kubectl run -it --rm test --image=busybox --restart=Never -n <namespace> -- wget -q -O- <service-name>

# Get pod IPs and their labels
kubectl get pods -n <namespace> -o wide -L version

# Check pod labels
kubectl get pods -n <namespace> --show-labels

# Port-forward to specific pod (test green directly)
kubectl port-forward deployment/app-green 8080:8080 -n <namespace>
```

## Best Practices for Blue-Green Deployments

### ✅ DO:

1. **Use automation for switchover**:
   ```bash
   # Script to switch traffic
   kubectl patch service app-service -p '{"spec":{"selector":{"version":"green"}}}'
   ```

2. **Test green before switching**:
   ```yaml
   # Create test service for green
   apiVersion: v1
   kind: Service
   metadata:
     name: app-service-test
   spec:
     selector:
       app: myapp
       version: green  # Only green pods
   ```

3. **Use clear version labels**:
   ```yaml
   # Good labels
   labels:
     app: myapp
     version: blue    # Clear indication
     
   # Or timestamp
   labels:
     app: myapp
     version: "20240115-1830"  # Deployment timestamp
   ```

4. **Keep blue running for rollback**:
   ```bash
   # Don't delete blue immediately
   # Keep for quick rollback (1-24 hours)
   ```

5. **Monitor after switchover**:
   ```
   # Watch error rates, latency, traffic
   # for at least 15-30 minutes
   ```

### ❌ DON'T:

1. **Don't forget to update selector**:
   ```bash
   # Verify after deployment
   kubectl get endpoints app-service
   ```

2. **Don't delete blue too quickly**:
   ```bash
   # Bad: Delete blue immediately
   kubectl delete deployment app-blue
   
   # Good: Keep for rollback window
   # Delete after validation period
   ```

3. **Don't switch without testing**:
   ```bash
   # Always test green before switching
   # Use separate test service
   ```

4. **Don't use same label for both**:
   ```yaml
   # Bad: Both have version=v1
   # Can't distinguish
   ```

## Blue-Green Deployment Variations

### Variation 1: Weighted Traffic (Canary-style)

```bash
# Create two services
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: app-blue
spec:
  selector:
    version: blue
  ports:
  - port: 80
---
apiVersion: v1
kind: Service
metadata:
  name: app-green
spec:
  selector:
    version: green
  ports:
  - port: 80
EOF

# Use Ingress to split traffic 90/10
apiVersion: networking.k8s.io/v1
kind: Ingress
spec:
  rules:
  - http:
      paths:
      - path: /
        backend:
          service:
            name: app-blue
            weight: 90  # 90% to blue
      - path: /
        backend:
          service:
            name: app-green
            weight: 10  # 10% to green
```

### Variation 2: Blue-Green with Database Migrations

```bash
# 1. Deploy green with backward-compatible code
kubectl apply -f green-deployment.yaml

# 2. Run database migration (forward-compatible)
kubectl exec -it migration-job -- ./migrate.sh

# 3. Switch traffic to green
kubectl patch service app-service -p '{"spec":{"selector":{"version":"green"}}}'

# 4. Keep blue running (can still work with new schema)
# 5. After validation, delete blue
```

### Variation 3: Instant Rollback

```bash
# Rollback: Just switch selector back
kubectl patch service app-service -p '{"spec":{"selector":{"version":"blue"}}}'

# Instant! No re-deployment needed
# This is the main advantage of blue-green
```

## What's Next?

You've learned how to use blue-green deployments for instant traffic switching and safe rollbacks.

Next level: Canary deployments! You'll learn how incorrect replica ratios can affect canary testing accuracy.

**Key takeaway**: In blue-green deployments, deploying the new version is only half the job - you must also update the service selector to route traffic to it!
