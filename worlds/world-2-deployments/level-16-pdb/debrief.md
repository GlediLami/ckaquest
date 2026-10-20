# 🎓 Mission Debrief: PDB Blocks All Evictions

## What Happened

Your PodDisruptionBudget (PDB) was configured with `minAvailable: 3` for a deployment with 3 replicas.

This created an impossible requirement: "Keep all 3 pods available while trying to evict one" - mathematically impossible!

Result: **All voluntary pod evictions were blocked**, preventing node maintenance, cluster upgrades, and autoscaling operations.

## How Kubernetes Behaved

**PDB Evaluation Process**:

```
Node drain requested (kubectl drain node-1)
    ↓
Kubernetes needs to evict pods on node-1
    ↓
Checks PDB for db-proxy pods
    ↓
PDB says: minAvailable = 3
Current healthy pods = 3
If we evict 1 pod: 3 - 1 = 2
Is 2 >= 3? NO ❌
    ↓
Eviction denied!
    ↓
Node drain FAILS
```

**What operations were blocked**:

```
❌ kubectl drain node → "Cannot evict pod: would violate PDB"
❌ Cluster upgrade → Cannot drain nodes
❌ Autoscaler scale-down → Cannot remove nodes
❌ Node maintenance → Stuck waiting
```

**With fixed PDB** (`minAvailable: 2`):

```
Node drain requested
    ↓
PDB says: minAvailable = 2
Current healthy pods = 3
If we evict 1 pod: 3 - 1 = 2
Is 2 >= 2? YES ✅
    ↓
Eviction allowed!
    ↓
Pod evicted, rescheduled on another node
    ↓
Node drain succeeds
```

## The Correct Mental Model

### PodDisruptionBudget Purpose

**PDBs protect applications from voluntary disruptions**:

| Voluntary Disruptions (PDB applies) | Involuntary Disruptions (PDB doesn't apply) |
|-------------------------------------|---------------------------------------------|
| `kubectl drain` | Node crash |
| Cluster upgrades | Node hardware failure |
| Autoscaler scale-down | Pod killed by OOMKiller |
| Node decommissioning | Network partition |

PDBs ensure that during planned maintenance, you maintain minimum service availability.

### minAvailable vs maxUnavailable

```yaml
# Option 1: minAvailable (absolute number)
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 2  # Keep at least 2 pods running
  selector:
    matchLabels:
      app: myapp

# Option 2: minAvailable (percentage)
spec:
  minAvailable: 67%  # Keep at least 67% running

# Option 3: maxUnavailable (absolute number)
spec:
  maxUnavailable: 1  # Allow at most 1 pod unavailable

# Option 4: maxUnavailable (percentage)
spec:
  maxUnavailable: 33%  # Allow at most 33% unavailable
```

**Relationship** (for 3 replicas):

```
minAvailable: 2  ===  maxUnavailable: 1
  (keep 2)              (lose 1)

minAvailable: 3  ===  maxUnavailable: 0
  (keep all) ❌         (lose none) ❌
  BLOCKS EVICTIONS!
```

### Configuration Guidelines

| Replicas | minAvailable | maxUnavailable | Evictions Allowed | Use Case |
|----------|--------------|----------------|-------------------|----------|
| 3 | 2 | 1 | 1 pod | Recommended |
| 3 | 3 | 0 | 0 pods ❌ | BLOCKS EVERYTHING |
| 5 | 3 | 2 | 2 pods | Good for larger deployments |
| 10 | 70% | 30% | 3 pods | Good for percentage-based |

**Rule of thumb**: Always allow at least 1 eviction!

```
minAvailable < total replicas
OR
maxUnavailable >= 1
```

## Real-World Incident Example

**Company**: Financial services platform (24/7 uptime requirement)  
**Impact**: 6-hour cluster upgrade delay, missed security patch window  
**Cost**: Security compliance violation ($250K fine) + emergency weekend work  

**What happened**:

The company had a critical Kubernetes cluster upgrade scheduled (security patches for a CVE). The SRE team started the rolling node upgrade at 2 AM (low-traffic window).

**PDB configuration** (set by a well-meaning developer):

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payment-service-pdb
spec:
  minAvailable: 5  # "Always keep all 5 pods for payment service!"
  selector:
    matchLabels:
      app: payment-service
---
# Deployment had exactly 5 replicas
spec:
  replicas: 5
```

Developer's logic: "Payment is critical, we need ALL 5 pods always running!"

**The cascade** (Saturday, 2 AM):

```
02:00 - Start cluster upgrade (using kops rolling-update)
02:01 - Attempt to drain first node (has 1 payment-service pod)
02:01 - kubectl drain node-1
02:01 - Eviction request for payment-service-xxx
02:01 - PDB check: minAvailable: 5, current: 5, after eviction: 4
02:01 - PDB denies eviction: "would violate policy"
02:01 - Node drain FAILS
02:01 - Automated upgrade pauses, alerts SRE
02:15 - SRE on-call investigates
02:30 - Identifies PDB blocking eviction
02:35 - Debates fixing PDB vs manual override
02:40 - Decides to temporarily delete PDB
02:41 - Delete PDB: kubectl delete pdb payment-service-pdb
02:42 - Resume node drain
02:45 - Node drain succeeds
02:50 - Payment pods rescheduled, all healthy
03:00 - Continue with upgrades
03:30 - Another node with payment pod...
03:30 - Realizes PDB was deleted, no protection!
03:35 - Recreate PDB with correct config (minAvailable: 4)
04:00 - Finish remaining nodes
08:00 - Upgrade complete (6 hours instead of planned 2 hours)
```

**Why it was problematic**:
- **Security window missed** - Needed to patch before Monday, barely made it
- **Compliance violation** - Required to patch within 48 hours of CVE disclosure
- **Emergency weekend work** - Team worked all night
- **Risk period** - 30 minutes with no PDB protection

**The proper fix**:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payment-service-pdb
spec:
  minAvailable: 4  # Allow 1 eviction, keep 4 running
  # OR equivalently:
  # maxUnavailable: 1
  selector:
    matchLabels:
      app: payment-service
```

**Process improvements implemented**:

1. **PDB validation in CI/CD**:
```bash
#!/bin/bash
# Reject PDBs that block all evictions
REPLICAS=$(yq '.spec.replicas' deployment.yaml)
MIN_AVAIL=$(yq '.spec.minAvailable' pdb.yaml)

if [ "$MIN_AVAIL" -ge "$REPLICAS" ]; then
    echo "ERROR: PDB minAvailable ($MIN_AVAIL) >= replicas ($REPLICAS)"
    echo "This blocks all evictions!"
    exit 1
fi
```

2. **Pre-upgrade PDB audit**:
```bash
# Check all PDBs before cluster upgrades
kubectl get pdb --all-namespaces -o json | \
  jq '.items[] | select(.status.disruptionsAllowed == 0) | .metadata.name'
# Alert if any PDB has disruptionsAllowed == 0
```

3. **Documentation**:
```
PDB Configuration Standard:
- minAvailable must be < total replicas
- Must allow at least 1 disruption
- Use minAvailable for absolute control
- Use maxUnavailable for percentage-based
```

**Lessons learned**:
1. **Test node drains before upgrades** - Don't discover PDB issues during upgrade
2. **PDBs should allow some evictions** - Otherwise they block maintenance
3. **Audit PDBs regularly** - Check disruptionsAllowed status
4. **Validate PDBs in CI/CD** - Catch misconfigurations before deployment

## Commands You Mastered

```bash
# List all PDBs
kubectl get pdb --all-namespaces

# Check PDB status
kubectl get pdb <name> -n <namespace>
# Look at ALLOWED column

# Describe PDB (see detailed status)
kubectl describe pdb <name> -n <namespace>

# Check if PDB allows any disruptions
kubectl get pdb <name> -n <namespace> -o jsonpath='{.status.disruptionsAllowed}'

# Edit PDB
kubectl edit pdb <name> -n <namespace>

# Test node drain (dry-run)
kubectl drain <node-name> --dry-run=server --ignore-daemonsets

# Actually drain a node
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# If stuck, see which pods block drain
kubectl drain <node-name> --dry-run=server

# View all PDBs and their disruption allowance
kubectl get pdb --all-namespaces -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name,MIN_AVAILABLE:.spec.minAvailable,MAX_UNAVAILABLE:.spec.maxUnavailable,ALLOWED:.status.disruptionsAllowed
```

## Best Practices for PDBs

### ✅ DO:

1. **Always allow some disruptions**:
   ```yaml
   # For 3 replicas
   spec:
     minAvailable: 2  # Allow 1 eviction ✅
   
   # NOT
   spec:
     minAvailable: 3  # Blocks all evictions ❌
   ```

2. **Use PDBs for all production deployments**:
   ```yaml
   # Protect against accidental mass evictions
   apiVersion: policy/v1
   kind: PodDisruptionBudget
   metadata:
     name: myapp-pdb
   spec:
     minAvailable: 2
     selector:
       matchLabels:
         app: myapp
   ```

3. **Test node drains before major operations**:
   ```bash
   # Dry-run to check PDBs
   kubectl drain node-1 --dry-run=server
   ```

4. **Use percentages for large deployments**:
   ```yaml
   # For 50+ replicas
   spec:
     minAvailable: 80%  # Keep 80% running
   ```

5. **Monitor PDB status**:
   ```bash
   # Alert if any PDB blocks all disruptions
   kubectl get pdb --all-namespaces -o json | \
     jq '.items[] | select(.status.disruptionsAllowed == 0)'
   ```

### ❌ DON'T:

1. **Don't set minAvailable == replicas**:
   ```yaml
   # WRONG - blocks all evictions
   spec:
     replicas: 3
   ---
   spec:
     minAvailable: 3  # Can't evict any pod!
   ```

2. **Don't set maxUnavailable: 0**:
   ```yaml
   # WRONG - same problem
   spec:
     maxUnavailable: 0  # Blocks evictions
   ```

3. **Don't forget PDBs for critical services**:
   ```
   # Missing PDB = no protection during disruptions
   # Someone might drain node and take down all pods!
   ```

4. **Don't use PDBs for single-replica deployments**:
   ```yaml
   # Pointless for replicas: 1
   # Either minAvailable: 1 (blocks evictions)
   # or minAvailable: 0 (no protection)
   ```

## PDB Configuration Matrix

### For Different Replica Counts

**3 replicas** (common for small services):
```yaml
spec:
  minAvailable: 2        # Keep 2, allow 1 eviction
  # OR
  maxUnavailable: 1      # Same thing
```

**5 replicas** (medium services):
```yaml
spec:
  minAvailable: 3        # Keep 3, allow 2 evictions
  # OR
  maxUnavailable: 2
```

**10+ replicas** (larger services):
```yaml
spec:
  minAvailable: 70%      # Keep 70%, allow 30% evictions
  # OR
  maxUnavailable: 30%
```

**Critical services** (payment, auth):
```yaml
spec:
  minAvailable: 80%      # More conservative
  # Always keep majority running
```

## What's Next?

You've learned how to configure PodDisruptionBudgets to protect applications while allowing necessary maintenance operations.

Next level: Blue-Green deployments! You'll learn how service selector misconfigurations can cause traffic routing issues.

**Key takeaway**: PDBs must allow at least 1 eviction, otherwise they block all maintenance operations. Balance protection with operational flexibility!
