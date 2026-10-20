# 🎯 World 2: Deployments & Scaling - Quick Reference Card

> **Advanced deployment patterns and scaling strategies**

## 🔧 Essential kubectl Commands

### Deployment Operations
```bash
# List deployments
kubectl get deployments -n ckaquest

# Detailed deployment info
kubectl describe deployment <name> -n ckaquest

# Check deployment rollout status
kubectl rollout status deployment/<name> -n ckaquest

# View rollout history
kubectl rollout history deployment/<name> -n ckaquest

# Rollback to previous version
kubectl rollout undo deployment/<name> -n ckaquest

# Rollback to specific revision
kubectl rollout undo deployment/<name> --to-revision=2 -n ckaquest

# Pause rollout (for canary/staged deployment)
kubectl rollout pause deployment/<name> -n ckaquest

# Resume rollout
kubectl rollout resume deployment/<name> -n ckaquest

# Restart deployment (rolling restart)
kubectl rollout restart deployment/<name> -n ckaquest
```

### Scaling Operations
```bash
# Scale deployment manually
kubectl scale deployment <name> --replicas=5 -n ckaquest

# Check HorizontalPodAutoscaler
kubectl get hpa -n ckaquest

# Detailed HPA status
kubectl describe hpa <name> -n ckaquest

# Watch HPA in action
kubectl get hpa -n ckaquest -w

# Check metrics (requires metrics-server)
kubectl top nodes
kubectl top pods -n ckaquest
```

### ReplicaSet Operations
```bash
# List ReplicaSets (usually managed by Deployments)
kubectl get replicasets -n ckaquest
kubectl get rs -n ckaquest

# Describe ReplicaSet
kubectl describe rs <name> -n ckaquest

# See which ReplicaSet owns which pods
kubectl get pods -n ckaquest -o wide --show-labels
```

### StatefulSet Operations
```bash
# List StatefulSets
kubectl get statefulsets -n ckaquest
kubectl get sts -n ckaquest

# Describe StatefulSet
kubectl describe sts <name> -n ckaquest

# Check PVCs for StatefulSet
kubectl get pvc -n ckaquest
```

### PodDisruptionBudget
```bash
# List PDBs
kubectl get pdb -n ckaquest

# Describe PDB (shows allowed disruptions)
kubectl describe pdb <name> -n ckaquest
```

### Probes & Health Checks
```bash
# Check pod readiness
kubectl get pods -n ckaquest -o wide

# See why pod is not ready
kubectl describe pod <name> -n ckaquest | grep -A 10 Conditions

# Check recent probe failures
kubectl describe pod <name> -n ckaquest | grep -i probe

# View events for probe failures
kubectl get events -n ckaquest | grep -i probe
```

---

## 🚨 Debugging Flowchart

```
Deployment Issues?
    │
    ├─→ Pods not starting
    │   ├─→ Check: kubectl get pods -n ckaquest
    │   ├─→ Check: kubectl describe deployment -n ckaquest
    │   ├─→ Look for: ImagePullBackOff, CrashLoopBackOff
    │   └─→ Fix: Fix image, fix command, check probes
    │
    ├─→ Rollout stuck/slow
    │   ├─→ Check: kubectl rollout status deployment/<name>
    │   ├─→ Check: kubectl describe deployment (Strategy section)
    │   ├─→ Look for: maxUnavailable=0, PDB blocking, failing probes
    │   └─→ Fix: Adjust strategy, check PDB, fix health checks
    │
    ├─→ Old pods still running
    │   ├─→ Check: kubectl get rs -n ckaquest
    │   ├─→ Check: kubectl describe deployment (Selector)
    │   ├─→ Look for: Label selector mismatch, manual ReplicaSets
    │   └─→ Fix: Update labels, delete old ReplicaSets
    │
    ├─→ HPA not scaling
    │   ├─→ Check: kubectl describe hpa -n ckaquest
    │   ├─→ Check: kubectl top pods -n ckaquest
    │   ├─→ Look for: metrics-server missing, no resource requests
    │   └─→ Fix: Install metrics-server, add requests to pods
    │
    ├─→ Probes failing
    │   ├─→ Check: kubectl describe pod (Events)
    │   ├─→ Check: kubectl logs <pod>
    │   ├─→ Look for: Wrong port, slow startup, timeout too short
    │   └─→ Fix: Correct probe config, add initialDelaySeconds
    │
    └─→ Data loss in StatefulSet
        ├─→ Check: kubectl get pvc -n ckaquest
        ├─→ Check: StatefulSet vs Deployment usage
        ├─→ Look for: Deployment used instead of StatefulSet
        └─→ Fix: Convert to StatefulSet, use volumeClaimTemplates
```

---

## 💡 Common Patterns & Solutions

### Pattern 1: Rollback Gone Wrong
**Symptoms:** `kubectl rollout undo` doesn't fix the issue  
**First Check:** `kubectl rollout history deployment/<name>`  
**Common Causes:**
- Rolling back to wrong revision
- Issue exists in multiple revisions
- History limit too small

**Quick Fix Template:**
```bash
# See all revisions
kubectl rollout history deployment/myapp -n ckaquest

# Check specific revision
kubectl rollout history deployment/myapp --revision=3 -n ckaquest

# Rollback to known good revision
kubectl rollout undo deployment/myapp --to-revision=2 -n ckaquest
```

### Pattern 2: Liveness Probe Killing Pods
**Symptoms:** Pods restart frequently, "Liveness probe failed" in events  
**First Check:** `kubectl describe pod <pod>` (Events section)  
**Common Causes:**
- Probe checks too soon (app still starting)
- Timeout too short
- Wrong endpoint or port

**Quick Fix Template:**
```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 30  # ✅ Wait for app to start
  periodSeconds: 10
  timeoutSeconds: 5        # ✅ Give endpoint time to respond
  failureThreshold: 3      # ✅ Allow some failures before restart
```

### Pattern 3: Readiness Probe Missing
**Symptoms:** Traffic sent to pods before ready, 5xx errors  
**First Check:** `kubectl get pods -n ckaquest` (READY column)  
**Common Causes:**
- No readiness probe configured
- Probe always fails
- Race condition during startup

**Quick Fix Template:**
```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 10  # ✅ Wait a bit
  periodSeconds: 5         # ✅ Check frequently
  successThreshold: 1      # ✅ Ready after 1 success
  failureThreshold: 3
```

### Pattern 4: HPA Can't Get Metrics
**Symptoms:** HPA shows `<unknown>` for metrics  
**First Check:** `kubectl describe hpa <name>`  
**Common Causes:**
- metrics-server not installed
- No resource requests on pods
- metrics-server not ready

**Quick Fix Template:**
```yaml
# Deployment MUST have resource requests for HPA
resources:
  requests:
    cpu: 100m      # ✅ HPA needs this to calculate %
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi
---
# HPA references the requests
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef:
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50  # % of requests.cpu
```

### Pattern 5: Rollout Strategy Wrong
**Symptoms:** Downtime during deployment, or rollout too slow  
**First Check:** `kubectl describe deployment` (Strategy section)  
**Common Causes:**
- maxUnavailable set to 0 or too low
- maxSurge set to 0
- Wrong strategy type

**Quick Fix Template:**
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1    # ✅ Allow 1 pod down at a time
    maxSurge: 1          # ✅ Allow 1 extra pod during rollout
# For zero-downtime:
# maxUnavailable: 0      # Never less than desired
# maxSurge: 1            # Create new before killing old
```

### Pattern 6: PodDisruptionBudget Blocking
**Symptoms:** Can't drain node, evictions blocked  
**First Check:** `kubectl describe pdb -n ckaquest`  
**Common Causes:**
- minAvailable too high for number of replicas
- maxUnavailable too low (0)
- Selector matches all pods

**Quick Fix Template:**
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 2        # ✅ Need at least 2 running
  # OR use:
  # maxUnavailable: 1    # ✅ Allow 1 pod to be down
  selector:
    matchLabels:
      app: myapp
# Make sure you have MORE replicas than minAvailable!
```

### Pattern 7: Blue-Green Selector Wrong
**Symptoms:** Service routes to old version or no pods  
**First Check:** `kubectl get svc <name> -o wide`  
**Common Causes:**
- Service selector doesn't match deployment labels
- Forgot to update service selector
- Both versions selected at once

**Quick Fix Template:**
```yaml
# Blue Deployment
metadata:
  labels:
    app: myapp
    version: blue
---
# Green Deployment  
metadata:
  labels:
    app: myapp
    version: green
---
# Service switches between them
spec:
  selector:
    app: myapp
    version: green  # ✅ Route to green only
```

### Pattern 8: Canary Imbalance
**Symptoms:** Wrong traffic split between versions  
**First Check:** `kubectl get pods -n ckaquest --show-labels`  
**Common Causes:**
- Wrong replica counts
- Labels not matching service selector
- Both deployments have same labels

**Quick Fix Template:**
```bash
# 90% stable, 10% canary:
kubectl scale deployment/stable --replicas=9 -n ckaquest
kubectl scale deployment/canary --replicas=1 -n ckaquest

# Both MUST have same service selector labels
# Service distributes evenly across ALL matching pods
```

---

## 🎓 Pro Tips

### Tip 1: Check Rollout Progress
```bash
# Watch rollout in real-time
kubectl rollout status deployment/myapp -n ckaquest -w

# See which ReplicaSets are active
kubectl get rs -n ckaquest -l app=myapp

# Old ReplicaSets have 0 pods
```

### Tip 2: Debug Probe Failures
```bash
# Test liveness/readiness endpoint manually
kubectl exec -it <pod> -n ckaquest -- wget -O- http://localhost:8080/healthz

# Check probe configuration
kubectl get pod <pod> -n ckaquest -o yaml | grep -A 10 livenessProbe
```

### Tip 3: Force Immediate Rollout
```bash
# Change something to trigger rollout
kubectl set image deployment/myapp app=myapp:v2 -n ckaquest

# Or force restart
kubectl rollout restart deployment/myapp -n ckaquest
```

### Tip 4: Check HPA Metrics
```bash
# Current CPU/memory usage
kubectl top pods -n ckaquest

# HPA decision-making info
kubectl describe hpa -n ckaquest | grep -A 5 Metrics
```

### Tip 5: Understand ReplicaSet Ownership
```bash
# See which Deployment owns which ReplicaSet
kubectl get rs -n ckaquest -o wide

# ReplicaSet name format: <deployment-name>-<template-hash>
```

---

## 📊 Deployment Strategy Comparison

| Strategy | Use Case | Downtime | Cost | Rollback Speed |
|----------|----------|----------|------|----------------|
| **RollingUpdate** | Most deployments | Zero | Low | Medium |
| **Recreate** | Stateful apps (old pattern) | Yes | Low | Slow |
| **Blue-Green** | Zero-downtime critical apps | Zero | High (2x) | Instant |
| **Canary** | Risk mitigation, gradual rollout | Zero | Medium | Fast |

---

## 🎯 Probe Types Reference

| Probe Type | Purpose | When to Use |
|------------|---------|-------------|
| **Liveness** | Is container alive? | Detect deadlocks, restart frozen apps |
| **Readiness** | Can container serve traffic? | Prevent traffic to unready pods |
| **Startup** | Has container started? | Slow-starting apps (avoid liveness kill) |

**Rule of Thumb:**
- Always use **readiness** for apps behind services
- Use **liveness** only if app can deadlock/freeze
- Use **startup** for apps that take >30s to start

---

## 📏 Resource Requests vs Limits

```yaml
resources:
  requests:      # Guaranteed minimum (for scheduling)
    cpu: 100m    # 0.1 CPU core
    memory: 128Mi
  limits:        # Maximum allowed (for enforcement)
    cpu: 200m
    memory: 256Mi
```

**Key Points:**
- **Requests**: Used for scheduling and HPA calculations
- **Limits**: Enforced by kubelet (OOMKill if exceeded)
- **HPA**: Scales based on % of REQUESTS, not limits
- **Best Practice**: Set both, limits = 2x requests for burstable workloads

---

## 🎯 Learning Objectives - World 2

By completing World 2, you should be able to:

- ✅ **Rollback Deployments** - Undo failed deployments, find good revisions
- ✅ **Configure Liveness Probes** - Prevent probe-induced restart loops
- ✅ **Configure Readiness Probes** - Ensure zero-downtime deployments
- ✅ **Debug HPA Issues** - Install metrics-server, configure autoscaling
- ✅ **Optimize Rollout Strategy** - Balance speed vs stability
- ✅ **Work with PodDisruptionBudgets** - Ensure availability during maintenance
- ✅ **Implement Blue-Green Deployments** - Instant rollback capability
- ✅ **Implement Canary Deployments** - Gradual traffic shifting
- ✅ **Choose StatefulSet vs Deployment** - Understand stateful workloads
- ✅ **Avoid Manual ReplicaSet Management** - Let Deployments handle it

---

## 📚 Additional Resources

### Official Kubernetes Docs
- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Rolling Updates](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/)
- [Configure Liveness/Readiness Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [HPA Walkthrough](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)

### CKAQuest Resources
- World 1 Quick Reference (basic kubectl commands)
- Use `guide` for deployment-specific walkthroughs
- Read debriefs for production incident case studies

---

## 🚀 Quick Wins Checklist

When stuck on a level, try these in order:

- [ ] `kubectl get deployments,rs,pods -n ckaquest` - See the full picture
- [ ] `kubectl describe deployment <name> -n ckaquest` - Check strategy, events
- [ ] `kubectl rollout status deployment/<name> -n ckaquest` - Is it progressing?
- [ ] `kubectl get events -n ckaquest --sort-by='.lastTimestamp'` - Recent activity
- [ ] `kubectl describe pod <pod> -n ckaquest` - Check probe failures, resources
- [ ] `kubectl logs <pod> -n ckaquest` - Application errors?
- [ ] Compare `broken.yaml` vs expected behavior - What's misconfigured?
- [ ] Use `hints` in game - Progressive guidance
- [ ] Use `guide` in game - Complete walkthrough if needed

**Remember:** Deployments are powerful but complex. Understanding the mental model is more important than memorizing commands!

---

💡 **Pro Tip:** Practice rolling updates on a test deployment before production. Use `--record` flag to track changes in rollout history!

🎮 **Ready for advanced patterns?** Run `./play.sh` and master deployments!
