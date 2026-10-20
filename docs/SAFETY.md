# CKAQuest Safety Guards 🛡️

## Overview

CKAQuest includes comprehensive safety guards to protect you from accidentally breaking your Kubernetes cluster. These guards are **enabled by default** and strongly recommended for all users, especially beginners.

## What's Protected

### 🚫 Blocked Operations (Cannot Execute)

1. **Critical Namespace Deletion**
   ```bash
   # ❌ BLOCKED
   kubectl delete namespace kube-system
   kubectl delete namespace kube-public
   kubectl delete namespace kube-node-lease
   kubectl delete namespace default
   ```

2. **Node Operations**
   ```bash
   # ❌ BLOCKED
   kubectl delete node <node-name>
   kubectl drain node <node-name>
   kubectl cordon node <node-name>
   ```

3. **Cluster-Wide Deletions**
   ```bash
   # ❌ BLOCKED
   kubectl delete pods --all-namespaces
   kubectl delete deployments --all-namespaces
   ```

4. **CustomResourceDefinitions**
   ```bash
   # ❌ BLOCKED
   kubectl delete crd <crd-name>
   ```

5. **Cluster-Level RBAC**
   ```bash
   # ❌ BLOCKED
   kubectl delete clusterrole <name>
   kubectl delete clusterrolebinding <name>
   ```

### ⚠️  Operations Requiring Confirmation

1. **Namespace Deletion**
   ```bash
   # ⚠️  Asks for confirmation
   kubectl delete namespace ckaquest
   ```

2. **Delete All Resources**
   ```bash
   # ⚠️  Asks for confirmation
   kubectl delete pods --all -n ckaquest
   ```

3. **PersistentVolume Operations**
   ```bash
   # ⚠️  Asks for confirmation
   kubectl delete pv <pv-name>
   ```

## RBAC Configuration

CKAQuest uses Role-Based Access Control to limit what you can do:

### Namespace-Level Permissions

Full access within `ckaquest` namespace to:
- Pods, Services, ConfigMaps, Secrets
- Deployments, ReplicaSets, StatefulSets, DaemonSets
- Jobs, CronJobs
- Ingresses, NetworkPolicies
- PersistentVolumeClaims

### Cluster-Level Permissions

**Read-only** access to:
- Nodes (view cluster info)
- Namespaces (list available namespaces)
- StorageClasses (for storage challenges)
- Metrics (for observability challenges)

### What You CANNOT Do

- Modify resources outside `ckaquest` namespace
- Create or delete namespaces (except with confirmation)
- Modify cluster-level resources (CRDs, ClusterRoles, etc.)
- Delete or modify nodes
- Access secrets in other namespaces

## Setup

### Automatic Setup (Recommended)

RBAC is automatically configured when you run:
```bash
./install.sh
```

### Manual Setup

```bash
# Apply RBAC configuration
./rbac/setup-rbac.sh

# Or manually:
kubectl apply -f rbac/ckaquest-rbac.yaml
```

## Using Safety Guards

### In Python Engine (Automatic)

Safety guards are automatically active when using the Python game engine:
```bash
./play.sh
```

### Testing Safety Guards

Test if a command would be blocked:
```bash
python3 engine/safety.py kubectl delete namespace kube-system
# Output: 🚨 BLOCKED: Cannot delete critical system namespaces!

python3 engine/safety.py kubectl get pods -n ckaquest
# Output: ✅ Command passed safety checks
```

### View Safety Information

```bash
python3 engine/safety.py info
```

## Disabling Safety Guards

**⚠️  NOT RECOMMENDED** - But if you need to disable safety guards:

```bash
# Temporary (current session only)
export CKAQUEST_SAFETY=off
./play.sh

# To re-enable
unset CKAQUEST_SAFETY
# or
export CKAQUEST_SAFETY=on
```

## Why Safety Guards Matter

### Real-World Examples

**Scenario 1: The Accidental Namespace Delete**
```bash
# Developer meant to type:
kubectl delete deployment myapp -n ckaquest

# But accidentally typed:
kubectl delete namespace ckaquest
```
Without safety guards: Entire namespace gone, all work lost.
With safety guards: Prompted for confirmation, given chance to cancel.

**Scenario 2: The Copy-Paste Disaster**
```bash
# Copied from Stack Overflow for production:
kubectl delete pods --all-namespaces

# Ran in dev cluster by mistake
```
Without safety guards: All pods in all namespaces deleted.
With safety guards: Command blocked completely.

**Scenario 3: The Node Deletion**
```bash
# Trying to delete a pod, mistyped:
kubectl delete node kind-control-plane
```
Without safety guards: Entire cluster node removed.
With safety guards: Command blocked, cluster saved.

## Safety Guard Implementation

### Command Validation

Safety guards use regex pattern matching to detect dangerous commands BEFORE execution:

```python
# Example: Detect namespace deletion
pattern = r"kubectl\s+delete\s+namespace\s+(kube-system|default)"

# Check command against patterns
if matches_dangerous_pattern(command):
    block_command()
```

### RBAC Enforcement

Even if safety guard detection is bypassed, RBAC enforces limits:

```yaml
# Role only allows operations in ckaquest namespace
kind: Role
metadata:
  namespace: ckaquest
# Cannot affect other namespaces
```

## Troubleshooting

### "Command blocked by safety guards"

This is working as intended! The command you tried is dangerous. Options:
1. Review what you're trying to do
2. Make sure you're using `-n ckaquest` namespace
3. Check if you have a typo
4. If you really need this operation, see "Disabling Safety Guards" (not recommended)

### "Permission denied" errors

You may be trying to access resources outside the `ckaquest` namespace:

```bash
# ❌ Won't work
kubectl get pods -n default

# ✅ Works
kubectl get pods -n ckaquest
```

### Safety guards not working

Check if they're enabled:
```bash
echo $CKAQUEST_SAFETY
# Should be empty or "on"

# If it says "off", re-enable:
unset CKAQUEST_SAFETY
```

## Best Practices

1. **Always use `-n ckaquest` flag**
   ```bash
   kubectl get pods -n ckaquest
   kubectl apply -f myapp.yaml -n ckaquest
   ```

2. **Test changes before applying**
   ```bash
   # Dry-run first
   kubectl apply -f deployment.yaml --dry-run=client -n ckaquest
   
   # Then apply for real
   kubectl apply -f deployment.yaml -n ckaquest
   ```

3. **Use `kubectl apply` instead of `kubectl create`**
   ```bash
   # ❌ Fails if exists
   kubectl create -f deployment.yaml
   
   # ✅ Creates or updates
   kubectl apply -f deployment.yaml
   ```

4. **Check what will be deleted**
   ```bash
   # See what would be deleted
   kubectl delete pod <name> --dry-run=client -n ckaquest
   ```

5. **Keep safety guards enabled**
   - Only disable if you absolutely know what you're doing
   - Re-enable immediately after

## Contributing

When creating new challenges:
- Ensure they work within `ckaquest` namespace
- Don't require cluster-admin permissions
- Test with safety guards enabled
- Document any exceptions needed

## FAQ

**Q: Why can't I delete the default namespace?**
A: The default namespace is critical to Kubernetes. Deleting it would break many system components. Use `ckaquest` namespace instead.

**Q: Can I practice RBAC challenges with safety guards?**
A: Yes! You have full RBAC control within the `ckaquest` namespace. You just can't modify cluster-level RBAC.

**Q: What if I'm an experienced user?**
A: Safety guards still help prevent accidents. Even experts make typos. You can disable them if needed, but we recommend keeping them on.

**Q: Will this work on production clusters?**
A: CKAQuest is designed for LOCAL clusters only. Never run on production. Safety guards are an extra layer of protection, not a replacement for proper cluster isolation.

## Summary

Safety guards provide multiple layers of protection:

1. **Command validation** - Blocks dangerous patterns before execution
2. **RBAC enforcement** - Limits permissions at the cluster level
3. **Namespace isolation** - Restricts operations to `ckaquest`
4. **User confirmation** - Prompts for risky but allowed operations

Together, these make CKAQuest safe for beginners while still providing realistic Kubernetes experience.

---

**Remember:** The goal is learning, not breaking things. Safety guards let you experiment confidently! 🛡️
