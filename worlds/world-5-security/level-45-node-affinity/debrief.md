# 🎓 LEVEL 45 DEBRIEF: Node Affinity & Advanced Scheduling

**Congratulations!** You've mastered NodeAffinity - the key to intelligent pod placement in Kubernetes!

---

## 📊 What You Fixed

**The Problem:**
```yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
    - matchExpressions:
      - key: gpu-type  # ❌ Nodes don't have this label
        values: [nvidia-tesla]  # ❌ Wrong value
```

**Result:** Pod stuck Pending, "didn't match node affinity"

**The Solution:**
```yaml
# 1. Label node
kubectl label nodes kind-control-plane accelerator=gpu

# 2. Fix affinity
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
    - matchExpressions:
      - key: accelerator  # ✅ Matches node label
        values: [gpu]  # ✅ Correct value
```

**Result:** Pod schedules successfully on labeled node

---

## 🎯 Understanding NodeAffinity

### What is NodeAffinity?

**Definition:** Rules that constrain which nodes pods can be scheduled on, based on node labels.

**Use Cases:**
- GPU workloads → GPU nodes
- Memory-intensive apps → high-memory nodes
- Geographic requirements → region-specific nodes
- Cost optimization → spot instances for dev

### NodeAffinity vs NodeSelector

**NodeSelector (Simple):**
```yaml
spec:
  nodeSelector:
    accelerator: gpu
```
- Simple key-value matching
- Limited flexibility

**NodeAffinity (Advanced):**
```yaml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: accelerator
            operator: In
            values: [gpu, tpu]
```
- Multiple operators (In, NotIn, Exists, etc.)
- OR logic between terms
- Required vs Preferred
- More expressive

---

## 📝 NodeAffinity Types

### 1. Required (Hard Constraint)

```yaml
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
    - matchExpressions:
      - key: node-type
        operator: In
        values: [gpu]
```

**Behavior:**
- Pod MUST match or won't schedule
- Pod stays Pending if no match
- Hard requirement

### 2. Preferred (Soft Constraint)

```yaml
nodeAffinity:
  preferredDuringSchedulingIgnoredDuringExecution:
  - weight: 100  # 1-100, higher = more preferred
    preference:
      matchExpressions:
      - key: disk-type
        operator: In
        values: [ssd]
```

**Behavior:**
- Pod prefers but doesn't require
- Schedules elsewhere if no match
- Weight determines preference strength

### 3. Combining Both

```yaml
nodeAffinity:
  # MUST have GPU
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
    - matchExpressions:
      - key: accelerator
        operator: In
        values: [gpu]
  # PREFER us-west region
  preferredDuringSchedulingIgnoredDuringExecution:
  - weight: 100
    preference:
      matchExpressions:
      - key: region
        operator: In
        values: [us-west]
```

---

## 🔧 Match Expressions Operators

### In

```yaml
- key: node-type
  operator: In
  values: [gpu, tpu]
```
**Means:** node-type must be "gpu" OR "tpu"

### NotIn

```yaml
- key: environment
  operator: NotIn
  values: [test]
```
**Means:** environment must NOT be "test"

### Exists

```yaml
- key: gpu
  operator: Exists
```
**Means:** Node must have "gpu" label (any value)

### DoesNotExist

```yaml
- key: spot-instance
  operator: DoesNotExist
```
**Means:** Node must NOT have "spot-instance" label

### Gt (Greater Than)

```yaml
- key: cpu-cores
  operator: Gt
  values: ["16"]
```
**Means:** cpu-cores must be > 16

### Lt (Less Than)

```yaml
- key: age-days
  operator: Lt
  values: ["30"]
```
**Means:** age-days must be < 30

---

## 🎯 Real-World Examples

### Example 1: GPU Workload

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ml-training
spec:
  containers:
  - name: tensorflow
    image: tensorflow/tensorflow:latest-gpu
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: accelerator
            operator: In
            values: [nvidia-tesla-v100, nvidia-tesla-p100]
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        preference:
          matchExpressions:
          - key: accelerator
            operator: In
            values: [nvidia-tesla-v100]  # Prefer V100 over P100
```

### Example 2: High-Memory Database

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: postgres
spec:
  containers:
  - name: postgres
    image: postgres:13
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: memory-size
            operator: In
            values: [large, xlarge]
          - key: disk-type
            operator: In
            values: [ssd]
```

### Example 3: Regional Placement

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-server
spec:
  containers:
  - name: api
    image: myapi:latest
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 80
        preference:
          matchExpressions:
          - key: topology.kubernetes.io/region
            operator: In
            values: [us-west-2]
      - weight: 20
        preference:
          matchExpressions:
          - key: topology.kubernetes.io/zone
            operator: In
            values: [us-west-2a]
```

### Example 4: Avoid Spot Instances

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: critical-app
spec:
  containers:
  - name: app
    image: critical:latest
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: node.kubernetes.io/instance-type
            operator: NotIn
            values: [spot]
```

---

## 🔍 NodeSelectorTerms Logic

### OR Logic Between Terms

```yaml
nodeSelectorTerms:
- matchExpressions:  # Term 1
  - key: zone
    operator: In
    values: [us-west-1a]
- matchExpressions:  # Term 2  
  - key: zone
    operator: In
    values: [us-west-1b]
```

**Means:** (zone=us-west-1a) OR (zone=us-west-1b)

### AND Logic Within Term

```yaml
nodeSelectorTerms:
- matchExpressions:
  - key: gpu  # AND
    operator: Exists
  - key: memory  # AND
    operator: In
    values: [high]
```

**Means:** (has GPU label) AND (memory=high)

---

## 🚨 Common Mistakes

### Mistake 1: Wrong Label Key

```yaml
# ❌ Typo in label key
- key: accellerator  # Misspelled!
  operator: In
  values: [gpu]
```

**Fix:** Match exact label key on nodes

### Mistake 2: Case Sensitivity

```yaml
# ❌ Wrong case
- key: Environment  # Capital E
  values: [Production]  # Capital P

# Nodes have: environment=production (lowercase)
```

**Fix:** Labels are case-sensitive!

### Mistake 3: Forgetting to Label Nodes

```yaml
# ✅ Affinity configured
nodeAffinity:
  required...:
    - key: gpu

# ❌ But no nodes labeled!
```

**Fix:** `kubectl label nodes <node> gpu=true`

### Mistake 4: Using Only Preferred

```yaml
# ❌ Only preferred, no required
preferredDuringSchedulingIgnoredDuringExecution:
- weight: 100
  preference:
    matchExpressions:
    - key: gpu
      operator: Exists
```

If no GPU nodes available, pod might schedule on non-GPU node!

**Fix:** Use `required` for must-have constraints

---

## 🛡️ Best Practices

### 1. Use Standard Labels

```yaml
# ✅ Standard Kubernetes labels
topology.kubernetes.io/region: us-west-2
topology.kubernetes.io/zone: us-west-2a
node.kubernetes.io/instance-type: m5.2xlarge
kubernetes.io/arch: amd64
kubernetes.io/os: linux
```

### 2. Combine Required + Preferred

```yaml
nodeAffinity:
  required...:  # Must have
    - key: accelerator
      values: [gpu]
  preferred...:  # Nice to have
    - weight: 100
      preference:
        matchExpressions:
        - key: gpu-generation
          values: [latest]
```

### 3. Use Weights Wisely

```yaml
preferred...:
- weight: 100  # Most important
  preference:
    matchExpressions:
    - key: region
      values: [us-west]
- weight: 50  # Medium importance
  preference:
    matchExpressions:
    - key: zone
      values: [us-west-1a]
- weight: 10  # Nice to have
  preference:
    matchExpressions:
    - key: disk-type
      values: [nvme]
```

### 4. Document Label Schema

```yaml
# Example label schema for your cluster
# GPU nodes:
#   accelerator: gpu
#   gpu-type: nvidia-tesla-v100
#   gpu-count: "4"
#
# Memory nodes:
#   memory-size: xlarge  # 256GB+
#   memory-size: large   # 128GB+
```

---

## 🎯 Key Takeaways

1. **NodeAffinity = intelligent scheduling** - Match pods to appropriate nodes
2. **Required vs Preferred** - Hard vs soft constraints
3. **Label nodes first** - Affinity only works with labeled nodes
4. **Use standard labels** - Leverage Kubernetes built-in labels
5. **Combine with taints** - NodeAffinity + Taints = complete control
6. **Test thoroughly** - Verify pods schedule as expected
7. **Document labels** - Clear schema for your cluster

---

## 🚀 Next Steps

Now that you understand NodeAffinity, you're ready for:

- **Level 46:** Taints and Tolerations - the complement to affinity
- **Level 47:** PodDisruptionBudget - availability during updates
- **Level 48:** Admission Webhooks - advanced policy enforcement

---

**Excellent work!** You've mastered advanced pod scheduling! 🎉📍

## Exam angle

Label the node, then copy nodeAffinity from the docs:

```bash
k label node ckaquest-worker accelerator=gpu
k get pod gpu-workload -o wide
```

Bookmark: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity

Your notes: Node Affinity, Labels and Selectors
