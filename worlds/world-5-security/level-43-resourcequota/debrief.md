# 🎓 LEVEL 43 DEBRIEF: Kubernetes ResourceQuota & Resource Management

**Congratulations!** You've mastered ResourceQuota - essential for multi-tenant clusters and cost control!

---

## 📊 What You Fixed

**The Problem:**
```yaml
# Quota allows only 2 CPUs total
spec:
  hard:
    requests.cpu: "2"

# Pod requests 2.5 CPUs
resources:
  requests:
    cpu: "2500m"  # 2.5 CPUs > 2 quota = REJECTED!
```

**Result:** Pod stuck in Pending, "exceeded quota" error

**The Solution:**
```yaml
# Reduced to fit within quota
resources:
  requests:
    cpu: "500m"  # 0.5 CPUs < 2 quota = ACCEPTED ✅
    memory: "512Mi"
  limits:
    cpu: "1"
    memory: "1Gi"
```

**Result:** Pod schedules successfully, quota respected

---

## 🎯 Understanding ResourceQuota

### What is ResourceQuota?

**Definition:** Hard limits on aggregate resource consumption per namespace

**Purpose:**
1. **Multi-tenancy:** Fair resource sharing between teams
2. **Cost control:** Prevent runaway cloud bills
3. **Stability:** Protect cluster from resource exhaustion
4. **Capacity planning:** Enforce organizational policies

### Scope

- **Per-namespace:** Each namespace has its own quota
- **Aggregate:** Total across all objects in namespace
- **Enforced at creation:** Kubernetes rejects objects that would exceed quota

---

## 📦 Types of ResourceQuota

### 1. Compute Resource Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: production
spec:
  hard:
    # CPU Quotas
    requests.cpu: "10"  # Total CPU requests ≤ 10 cores
    limits.cpu: "20"  # Total CPU limits ≤ 20 cores
    
    # Memory Quotas
    requests.memory: "20Gi"  # Total memory requests ≤ 20Gi
    limits.memory: "40Gi"  # Total memory limits ≤ 40Gi
```

**What this enforces:**
- All pods combined can request max 10 CPUs
- All pods combined can limit max 20 CPUs  
- Same for memory

### 2. Storage Quotas

```yaml
spec:
  hard:
    # Storage quotas
    requests.storage: "500Gi"  # Total PVC requests
    persistentvolumeclaims: "10"  # Max 10 PVCs
```

### 3. Object Count Quotas

```yaml
spec:
  hard:
    # Object counts
    pods: "50"  # Max 50 pods
    services: "10"  # Max 10 services
    configmaps: "20"  # Max 20 ConfigMaps
    secrets: "20"  # Max 20 Secrets
    replicationcontrollers: "10"
    deployments.apps: "10"
    statefulsets.apps: "5"
```

### 4. Quota Scopes

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: best-effort-quota
spec:
  hard:
    pods: "10"
  scopes:
  - BestEffort  # Only pods with no requests/limits
```

**Scopes:**
- `Terminating`: Pods with activeDeadlineSeconds
- `NotTerminating`: Pods without activeDeadlineSeconds
- `BestEffort`: Pods with no requests/limits
- `NotBestEffort`: Pods with requests or limits

---

## ⚖️ Requests vs Limits

### Requests (Guaranteed Resources)

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
```

**What it means:**
- **Scheduler:** Node must have this available
- **Guarantee:** Kubernetes reserves these resources
- **QoS:** Determines Quality of Service class
- **Quota:** Counted against namespace quota

**When pod scheduled:**
- Kubernetes finds node with ≥500m CPU available
- Reserves 500m CPU and 512Mi memory
- Other pods can't use these reserved resources

### Limits (Maximum Resources)

```yaml
resources:
  limits:
    cpu: "1"
    memory: "1Gi"
```

**What it means:**
- **Maximum:** Container can't exceed this
- **CPU:** Throttled if exceeded (cgroups)
- **Memory:** Killed if exceeded (OOMKilled)
- **Quota:** Also counted against quota

**Enforcement:**
- **CPU:** Container throttled but stays running
- **Memory:** Container killed and restarted

### Request = Limit (QoS Guaranteed)

```yaml
resources:
  requests:
    memory: "1Gi"
  limits:
    memory: "1Gi"  # Same value
```

**Benefits:**
- **Guaranteed QoS class** - highest priority
- **Last to be evicted** under node pressure
- **Predictable** performance

---

## 🔢 Resource Units

### CPU Units

| Notation | Meaning | Cores |
|----------|---------|-------|
| `1` | 1 CPU core | 1.0 |
| `500m` | 500 millicores | 0.5 |
| `100m` | 100 millicores | 0.1 |
| `2500m` | 2500 millicores | 2.5 |
| `0.5` | Half core | 0.5 |

**1 CPU = 1000 millicores (m)**

### Memory Units

| Notation | Binary (Recommended) | Decimal |
|----------|---------------------|---------|
| 1 Kibibyte | `1Ki` = 1024 bytes | `1K` = 1000 bytes |
| 1 Mebibyte | `1Mi` = 1024² bytes | `1M` = 1000² bytes |
| 1 Gibibyte | `1Gi` = 1024³ bytes | `1G` = 1000³ bytes |
| 1 Tebibyte | `1Ti` = 1024⁴ bytes | `1T` = 1000⁴ bytes |

**Prefer:** Ki, Mi, Gi, Ti (binary, IEC standard)

---

## 🚨 REAL-WORLD HORROR STORY: The $200K Cloud Bill

### The Incident: Runaway Resource Consumption

**Company:** Startup scaling rapidly  
**Date:** March 2023  
**Impact:** $200K unexpected cloud bill, cluster collapse

### What Happened

**Setup:**
- Shared development Kubernetes cluster
- **No ResourceQuotas** configured
- All developers can deploy to any namespace

**The Timeline:**

**Monday 09:00** - Developer testing autoscaling feature  
**Monday 09:15** - Bug in autoscaler: scales to 1000 pods instead of 10  
**Monday 09:20** - Each pod requests 2 CPUs + 4Gi memory  
**Monday 09:25** - Cluster autoscaler sees resource pressure  
**Monday 09:30** - Autoscaler adds 50 new nodes (r5.4xlarge, $1.34/hr each)  
**Monday 09:35** - Still not enough, adds 50 more nodes  
**Monday 10:00** - 150 nodes running ($201/hour total)  
**Monday 11:00** - Other teams' pods evicted (resource pressure)  
**Monday 12:00** - Production services impacted  
**Monday 13:00** - Alarms finally noticed  
**Monday 13:30** - Emergency response, pods killed  
**Weekly Bill** - $28,944 for test workload (should have been ~$500)  
**Final Damage** - $200K over subscription bills before limits set

### Root Causes

1. **No ResourceQuotas** - Unlimited resource requests
2. **No review process** - Direct deploys to cluster
3. **No cost alerts** - Runaway spending undetected
4. **Shared cluster** - Production and dev mixed
5. **No LimitRanges** - No default resource limits

### The Fix That Would Have Prevented It

```yaml
# Development namespace quota
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: development
spec:
  hard:
    requests.cpu: "20"  # Max 20 CPUs total
    requests.memory: "40Gi"  # Max 40Gi memory
    pods: "100"  # Max 100 pods
    
---
# Also add LimitRange for defaults
apiVersion: v1
kind: LimitRange
metadata:
  name: dev-limits
  namespace: development
spec:
  limits:
  - max:
      cpu: "2"  # No pod > 2 CPUs
      memory: "4Gi"
    default:
      cpu: "100m"  # Default if not specified
      memory: "128Mi"
    type: Container
```

**With these quotas:**
- Developer's 1000 pods would be blocked at ~100 pods
- Maximum damage: 100 pods × 2 CPU = 200 CPUs (vs 2000 CPUs)
- Cost: ~$2,000 (vs $200,000) - 100x cheaper!
- Other teams unaffected

### Lessons Learned

1. **Always use ResourceQuotas** - Every namespace
2. **Separate dev and prod** - Different clusters or strict quotas
3. **Set default limits** - LimitRange for defaults
4. **Cost monitoring** - Alert on spending anomalies
5. **Review processes** - Don't allow direct deploys
6. **Pod limits** - Limit total pod count

---

## 🛡️ ResourceQuota Best Practices

### 1. Set Quotas on All Namespaces

```yaml
# Production - conservative
apiVersion: v1
kind: ResourceQuota
metadata:
  name: prod-quota
  namespace: production
spec:
  hard:
    requests.cpu: "50"
    requests.memory: "100Gi"
    pods: "200"

---
# Development - more generous
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: development
spec:
  hard:
    requests.cpu: "20"
    requests.memory: "40Gi"
    pods: "100"
```

### 2. Use LimitRange for Defaults

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
  - max:  # Maximum per container
      cpu: "2"
      memory: "4Gi"
    min:  # Minimum per container
      cpu: "10m"
      memory: "16Mi"
    default:  # If no limit specified
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:  # If no request specified
      cpu: "100m"
      memory: "128Mi"
    type: Container
```

### 3. Monitor Quota Usage

```bash
# Check all quotas
kubectl get resourcequota --all-namespaces

# Detailed quota status
kubectl describe resourcequota -n production

# Watch quota usage
watch kubectl get resourcequota -n production
```

### 4. Set Both Requests and Limits

```yaml
resources:
  requests:  # For scheduling
    cpu: "500m"
    memory: "512Mi"
  limits:  # For enforcement
    cpu: "1"
    memory: "1Gi"
```

### 5. Right-Size Resources

Don't over-request:
```yaml
# ❌ Too high (wastes quota)
requests:
  cpu: "4"
  memory: "8Gi"

# ✅ Right-sized
requests:
  cpu: "100m"  # Start small
  memory: "128Mi"
```

### 6. Use Vertical Pod Autoscaler (VPA)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Auto"  # Automatically right-size
```

---

## 🔍 Debugging Quota Issues

### Check Quota Status

```bash
kubectl describe resourcequota compute-quota -n k8squest
```

Output:
```
Name:            compute-quota
Namespace:       k8squest
Resource         Used  Hard
--------         ----  ----
limits.cpu       1     4
limits.memory    1Gi   4Gi
pods             1     10
requests.cpu     500m  2       ← Usage vs limit
requests.memory  512Mi 2Gi
```

### Check Pod Events

```bash
kubectl describe pod my-pod -n k8squest
```

Look for:
```
Warning  FailedScheduling  ... exceeded quota: compute-quota, requested: requests.cpu=2500m
```

### List All Pods in Namespace

```bash
# See what's using quota
kubectl get pods -n k8squest -o custom-columns=\
NAME:.metadata.name,\
CPU_REQ:.spec.containers[*].resources.requests.cpu,\
MEM_REQ:.spec.containers[*].resources.requests.memory
```

### Calculate Total Usage

```bash
# Sum all CPU requests
kubectl get pods -n k8squest -o jsonpath='{range .items[*]}{.spec.containers[*].resources.requests.cpu}{"\n"}{end}' | \
  sed 's/m$//' | awk '{s+=$1} END {print s "m"}'
```

---

## 📚 Quick Reference

### Common Quota Configurations

| Environment | CPU Requests | Memory Requests | Pods |
|-------------|--------------|-----------------|------|
| **Development** | 10-20 | 20-40Gi | 50-100 |
| **Staging** | 20-50 | 40-100Gi | 100-200 |
| **Production** | 50-200 | 100-500Gi | 200-1000 |

### Resource Sizing Guide

| Workload | CPU Request | Memory Request |
|----------|-------------|----------------|
| **Minimal** (sidecar) | 10m | 32Mi |
| **Small** (simple web) | 100m | 128Mi |
| **Medium** (typical app) | 500m | 512Mi |
| **Large** (database) | 2 | 4Gi |

---

## 🎯 Key Takeaways

1. **Use ResourceQuota everywhere** - Protect against runaway consumption
2. **Set realistic quotas** - Based on actual needs, not guesses
3. **Requests for scheduling** - Guarantees, counted against quota
4. **Limits for safety** - Maximum usage, prevent hogging
5. **Monitor quota usage** - Track how much is consumed
6. **Use LimitRange** - Set defaults for containers without requests/limits
7. **Right-size workloads** - Monitor actual usage, adjust accordingly
8. **Separate environments** - Different quotas for dev/staging/prod

---

## 🚀 Next Steps

Now that you understand ResourceQuotas, you're ready for:

- **Level 44:** NetworkPolicy - controlling network traffic
- **Level 45:** Node Affinity - advanced pod scheduling
- **Level 46:** Taints and Tolerations - node scheduling constraints

---

**Well done!** You've mastered resource management - critical for production Kubernetes clusters! 🎉💰
