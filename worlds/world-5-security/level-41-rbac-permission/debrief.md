# 🎓 LEVEL 41 DEBRIEF: Kubernetes RBAC (Role-Based Access Control)

**Congratulations!** You've mastered Kubernetes RBAC - the foundation of security and access control in production clusters!

---

## 📊 What You Fixed

**The Problem:**
```yaml
# ServiceAccount exists
apiVersion: v1
kind: ServiceAccount
metadata:
  name: pod-reader

# ❌ No Role - no permissions defined
# ❌ No RoleBinding - ServiceAccount not granted anything
```

**Result:** Pod crashes with "Forbidden: pods is forbidden"

**The Solution:**
```yaml
# 1. Define permissions
kind: Role
rules:
- resources: ["pods"]
  verbs: ["get", "list", "watch"]

# 2. Grant permissions
kind: RoleBinding
roleRef:
  name: pod-reader-role
subjects:
- kind: ServiceAccount
  name: pod-reader
```

**Result:** Pod successfully lists pods with proper RBAC permissions

---

## 🔍 Understanding RBAC

### The Four RBAC Components

**1. ServiceAccount** (WHO - Identity)
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  namespace: default
```
- Identity for pods
- Like a "user account" for applications
- Each pod uses a ServiceAccount (default: "default")

**2. Role** (WHAT - Permissions, Namespace-scoped)
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```
- Defines what actions are allowed
- Namespace-specific
- Doesn't grant anything by itself

**3. RoleBinding** (WHO gets WHAT - Grant)
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: pod-reader
subjects:
- kind: ServiceAccount
  name: my-app
  namespace: default
```
- Connects Role to ServiceAccount
- Grants the permissions
- Namespace-specific

**4. ClusterRole & ClusterRoleBinding** (Cluster-wide)
```yaml
kind: ClusterRole  # Cluster-wide permissions
kind: ClusterRoleBinding  # Cluster-wide grant
```
- Not namespace-specific
- For cluster-scoped resources (nodes, namespaces, etc.)

---

## 🎯 RBAC in Action

### Example 1: Read-Only Pod Access

```yaml
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: pod-viewer
  namespace: production
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: view-pods
  namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: pod-reader
subjects:
- kind: ServiceAccount
  name: pod-viewer
  namespace: production
```

**Use Case:** Monitoring application that needs to read pod status

### Example 2: Deployment Manager

```yaml
kind: Role
metadata:
  name: deployment-manager
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]  # Read-only pods
```

**Use Case:** CI/CD system deploying applications

### Example 3: Secret Reader

```yaml
kind: Role
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
  resourceNames: ["database-password"]  # Only specific secret
```

**Use Case:** Application needs access to specific secret only

### Example 4: Multiple Permissions

```yaml
kind: Role
metadata:
  name: app-manager
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "update", "patch"]
```

**Use Case:** Application management platform

---

## 🔑 RBAC Verbs (Actions)

| Verb | Description | HTTP Method |
|------|-------------|-------------|
| **get** | Read a single resource | GET |
| **list** | List resources | GET |
| **watch** | Watch for changes | GET (stream) |
| **create** | Create new resource | POST |
| **update** | Replace resource | PUT |
| **patch** | Modify resource | PATCH |
| **delete** | Delete resource | DELETE |
| **deletecollection** | Delete multiple | DELETE |

**Common Combinations:**
- **Read-only:** get, list, watch
- **Full access:** get, list, watch, create, update, patch, delete
- **Create-only:** create
- **Update-only:** update, patch

---

## 📦 API Groups & Resources

### Core API Group ("")

```yaml
rules:
- apiGroups: [""]  # Core group
  resources:
  - pods
  - services
  - configmaps
  - secrets
  - persistentvolumeclaims
  - namespaces
```

### Apps API Group

```yaml
rules:
- apiGroups: ["apps"]
  resources:
  - deployments
  - statefulsets
  - daemonsets
  - replicasets
```

### Batch API Group

```yaml
rules:
- apiGroups: ["batch"]
  resources:
  - jobs
  - cronjobs
```

### RBAC API Group

```yaml
rules:
- apiGroups: ["rbac.authorization.k8s.io"]
  resources:
  - roles
  - rolebindings
  - clusterroles
  - clusterrolebindings
```

---

## 💥 Common RBAC Mistakes

### Mistake 1: No RoleBinding

```yaml
# Have ServiceAccount ✅
# Have Role ✅
# No RoleBinding ❌

# Result: Permission denied!
```

**Fix:** Create RoleBinding to connect them

### Mistake 2: Wrong Namespace

```yaml
# ServiceAccount in namespace: production
kind: ServiceAccount
metadata:
  namespace: production

# RoleBinding in namespace: default  ❌
kind: RoleBinding
metadata:
  namespace: default  # Wrong namespace!
```

**Fix:** Match namespaces

### Mistake 3: Wrong API Group

```yaml
rules:
- apiGroups: [""]  # ❌ Wrong! Deployments not in core
  resources: ["deployments"]
```

**Fix:**
```yaml
rules:
- apiGroups: ["apps"]  # ✅ Deployments in apps group
  resources: ["deployments"]
```

### Mistake 4: Missing Verbs

```yaml
rules:
- resources: ["pods"]
  verbs: ["get"]  # ❌ Can get but not list!
```

Pod tries `kubectl get pods` (list) → Permission denied

**Fix:** Add list verb

### Mistake 5: Overly Permissive

```yaml
rules:
- apiGroups: ["*"]  # ❌ All API groups!
  resources: ["*"]  # ❌ All resources!
  verbs: ["*"]  # ❌ All actions!
# This is cluster-admin equivalent - too dangerous!
```

**Fix:** Grant only needed permissions (principle of least privilege)

---

## 🚨 REAL-WORLD HORROR STORY: The RBAC Misconfiguration

### The Incident: $2.1M Data Breach

**Company:** Financial services platform  
**Date:** August 2022  
**Impact:** Customer data exposed, $2.1M in fines and remediation

### What Happened

DevOps team created ServiceAccount for monitoring:

```yaml
# Intended: Read-only access to pods
kind: Role
metadata:
  name: monitor-role
rules:
- apiGroups: ["*"]  # ❌ Typo: meant [""]
  resources: ["pods"]
  verbs: ["get", "list"]  # ❌ But with apiGroups: ["*"]
```

**The Typo:**
- `apiGroups: [""]` = core API only
- `apiGroups: ["*"]` = **ALL API groups!**

**Result:**
- Monitoring ServiceAccount could access **all resources**
- Including secrets, configmaps with credentials
- Attacker compromised monitoring pod
- Extracted database credentials from secrets
- Accessed customer PII database

### The Timeline

**10:00** - Monitoring pod deployed with overly broad permissions  
**14:30** - Attacker gains access to monitoring pod (vulnerable dependency)  
**14:35** - Attacker discovers can list secrets  
**14:40** - Database credentials extracted  
**15:00** - Customer database accessed  
**15:30** - 250,000 customer records exfiltrated  
**18:00** - Anomaly detected in database access logs  
**20:00** - Breach confirmed, emergency response initiated  
**Next 6 months** - Investigation, fines, customer notification, lawsuits

### Root Causes

1. **Typo in RBAC configuration:** `["*"]` instead of `[""]`
2. **No review process:** Direct apply without peer review
3. **No RBAC auditing:** Overly broad permissions not detected
4. **Insufficient testing:** Never tested what permissions were actually granted
5. **No least privilege:** Should have used specific resourceNames

### The Fix

```yaml
# Correct configuration
kind: Role
metadata:
  name: monitor-role
rules:
- apiGroups: [""]  # ✅ Only core API
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
  # NO access to secrets!
```

**Additional Safeguards:**
1. RBAC policy review process
2. Automated RBAC auditing
3. Alert on overly broad permissions
4. Regular permission reviews
5. Use kubectl auth can-i to test

### Lessons Learned

1. **Review all RBAC changes** - Peer review required
2. **Test permissions** - kubectl auth can-i before deployment
3. **Audit regularly** - Check for overly broad permissions
4. **Principle of least privilege** - Grant only what's needed
5. **Monitor RBAC changes** - Alert on permission escalations

---

## 🛡️ RBAC Best Practices

### 1. Principle of Least Privilege

```yaml
# ❌ Too broad
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]

# ✅ Specific
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
  resourceNames: ["my-specific-pod"]  # Even more specific
```

### 2. Use Specific API Groups

```yaml
rules:
- apiGroups: [""]  # Core
  resources: ["pods"]
- apiGroups: ["apps"]  # Apps
  resources: ["deployments"]
```

### 3. Limit by Resource Names

```yaml
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
  resourceNames: ["app-secret"]  # Only this secret
```

### 4. Separate Read and Write

```yaml
# Read-only role
kind: Role
metadata:
  name: viewer
rules:
- verbs: ["get", "list", "watch"]

# Write role (if needed)
kind: Role
metadata:
  name: editor
rules:
- verbs: ["get", "list", "watch", "create", "update", "patch"]
```

### 5. Test Before Applying

```bash
# Test permissions
kubectl auth can-i list pods \
  --as=system:serviceaccount:default:my-app

# Test specific resource
kubectl auth can-i get secret database-password \
  --as=system:serviceaccount:default:my-app
```

### 6. Regular Audits

```bash
# List all RoleBindings
kubectl get rolebindings --all-namespaces

# Check who can do what
kubectl auth can-i --list \
  --as=system:serviceaccount:default:my-app
```

### 7. Use Built-in Roles When Possible

```yaml
roleRef:
  kind: ClusterRole
  name: view  # Built-in: read-only
  # Other built-in: edit, admin, cluster-admin
```

---

## 🎯 Key Takeaways

1. **RBAC = Role + RoleBinding** - Both required for permissions
2. **ServiceAccount = Identity** - What pods run as
3. **Test with kubectl auth can-i** - Verify permissions work
4. **Principle of least privilege** - Grant only what's needed
5. **Match namespaces** - ServiceAccount, Role, RoleBinding in same namespace
6. **Review RBAC changes** - Security critical, require review
7. **Audit regularly** - Check for overly broad permissions
8. **Use specific API groups** - Avoid wildcards

---

## 🚀 Next Steps

Now that you understand RBAC, you're ready for:

- **Level 42:** SecurityContext and privilege escalation
- **Level 43:** ResourceQuotas and limits
- **Level 44:** NetworkPolicy for traffic control

---

**Well done!** You've mastered Kubernetes RBAC - the foundation of cluster security! 🎉🔐
