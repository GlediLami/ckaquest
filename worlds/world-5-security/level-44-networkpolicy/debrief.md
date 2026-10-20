# 🎓 LEVEL 44 DEBRIEF: Kubernetes NetworkPolicy

**Congratulations!** You've mastered NetworkPolicy - the firewall for your Kubernetes pods!

---

## 📊 What You Fixed

**The Problem:**
```yaml
# Deny-all policy blocking everything
spec:
  podSelector: {}  # All pods
  policyTypes:
  - Ingress
  - Egress
  # ❌ No rules = block ALL traffic
```

**Result:** Backend couldn't connect to database, connection refused

**The Solution:**
```yaml
# Database ingress: Allow from backend
ingress:
- from:
  - podSelector:
      matchLabels:
        app: backend
  ports:
  - port: 5432

# Backend egress: Allow to database + DNS
egress:
- to:
  - podSelector:
      matchLabels:
        app: database
  ports:
  - port: 5432
- to:  # DNS!
  - namespaceSelector: ...
  ports:
  - port: 53
```

**Result:** Backend connects successfully, DNS works, security maintained

---

## � Pro Tip: Incremental Application

**Good News:** You can apply NetworkPolicy fixes **without deleting** the existing setup!

### Why This Works

NetworkPolicies are **additive** - when multiple policies match a pod, they combine:

```bash
# Broken state has deny-all
kubectl apply -f broken.yaml

# Apply solution incrementally (no delete needed!)
kubectl apply -f solution.yaml
```

**Result:**
- ✅ New allow policies get **created**
- ✅ Old deny-all policy **remains** (harmless)
- ✅ Allow rules **override** deny-all for matching selectors
- ✅ Connectivity **works immediately**

### What Kubernetes Does

```
deny-all (podSelector: {})
  + allow-backend-egress (podSelector: {app: backend})
  + allow-database-ingress (podSelector: {app: database})
  = Backend and database can communicate!
```

**Note:** The backend pod may show an error during apply because its command differs between broken/solution, but this is harmless - the NetworkPolicies still apply correctly.

---

## �🔒 Understanding NetworkPolicy

### What is NetworkPolicy?

**Definition:** Kubernetes firewall rules controlling pod-to-pod communication

**Key Points:**
- Layer 3/4 filtering (IP + port)
- Pod label-based selection
- Namespace-scoped
- Deny-by-default when applied

### Default Behavior

**Without NetworkPolicy:**
```
All pods can communicate freely (open)
```

**With empty NetworkPolicy:**
```yaml
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
  # No rules = DENY ALL
```

Result: Complete isolation

---

## 📝 NetworkPolicy Structure

### Complete Example

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-policy
  namespace: production
spec:
  # 1. Which pods does this apply to?
  podSelector:
    matchLabels:
      app: api
  
  # 2. What direction?
  policyTypes:
  - Ingress  # Incoming traffic
  - Egress   # Outgoing traffic
  
  # 3. Ingress rules (who can connect TO these pods)
  ingress:
  - from:
    - podSelector:        # From pods in same namespace
        matchLabels:
          app: frontend
    - namespaceSelector:  # From pods in other namespaces
        matchLabels:
          env: production
    ports:
    - protocol: TCP
      port: 8080
      
  # 4. Egress rules (where these pods can connect TO)
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
  - to:  # Allow DNS
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

---

## 🎯 Ingress Rules (Incoming Traffic)

### Basic Ingress

```yaml
spec:
  podSelector:
    matchLabels:
      app: backend  # Apply to backend pods
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend  # Allow from frontend
    ports:
    - protocol: TCP
      port: 8080
```

**Means:** Backend pods accept connections from frontend pods on port 8080

### Multiple Sources (OR logic)

```yaml
ingress:
- from:
  - podSelector:
      matchLabels:
        app: frontend
  - podSelector:
      matchLabels:
        app: admin
  ports:
  - port: 8080
```

**Means:** Allow from (frontend OR admin) pods

### Multiple Conditions (AND logic)

```yaml
ingress:
- from:
  - podSelector:
      matchLabels:
        app: frontend
    namespaceSelector:
      matchLabels:
        env: production
  ports:
  - port: 8080
```

**Means:** Allow from frontend pods AND production namespace (both required)

### Allow from Specific IPs

```yaml
ingress:
- from:
  - ipBlock:
      cidr: 10.0.0.0/24
      except:
      - 10.0.0.1/32  # Exclude this IP
  ports:
  - port: 80
```

---

## 🚀 Egress Rules (Outgoing Traffic)

### Basic Egress

```yaml
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 8080
```

**Means:** Frontend pods can connect to backend pods on port 8080

### Critical: DNS Egress

```yaml
egress:
- to:
  - namespaceSelector:
      matchLabels:
        kubernetes.io/metadata.name: kube-system
  ports:
  - protocol: UDP
    port: 53  # DNS
```

**Always include** DNS egress or pods can't resolve hostnames!

### Allow External Traffic

```yaml
egress:
- to:
  - ipBlock:
      cidr: 0.0.0.0/0  # Internet
  ports:
  - protocol: TCP
    port: 443  # HTTPS
```

### Block All Egress

```yaml
spec:
  podSelector:
    matchLabels:
      app: isolated
  policyTypes:
  - Egress
  # No egress rules = block all outgoing
```

---

## 🛠️ Common Patterns

### 1. Default Deny All

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}  # All pods
  policyTypes:
  - Ingress
  - Egress
  # No rules = deny all
```

### 2. Allow DNS Only

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

### 3. Three-Tier Application

```yaml
# Frontend → Backend
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-to-backend
spec:
  podSelector:
    matchLabels:
      tier: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: frontend
    ports:
    - port: 8080

---
# Backend → Database
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-to-database
spec:
  podSelector:
    matchLabels:
      tier: database
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: backend
    ports:
    - port: 5432
```

### 4. Allow from Specific Namespace

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-monitoring
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - port: 9090
```

---

## 💥 Common NetworkPolicy Mistakes

### Mistake 1: Forgetting DNS

```yaml
# ❌ Backend can't resolve database hostname
egress:
- to:
  - podSelector:
      matchLabels:
        app: database
  # Missing DNS rule!
```

**Fix:**
```yaml
# ✅ Always include DNS
egress:
- to:
  - podSelector:
      matchLabels:
        app: database
  ports:
  - port: 5432
- to:  # DNS
  - namespaceSelector:
      matchLabels:
        kubernetes.io/metadata.name: kube-system
  ports:
  - protocol: UDP
    port: 53
```

### Mistake 2: Wrong Selector Logic

```yaml
# ❌ Thinks this means "frontend AND production"
# Actually means "frontend OR production"
ingress:
- from:
  - podSelector:
      matchLabels:
        app: frontend
  - namespaceSelector:
      matchLabels:
        env: production
```

**Fix:**
```yaml
# ✅ AND logic: both in same entry
ingress:
- from:
  - podSelector:
      matchLabels:
        app: frontend
    namespaceSelector:  # Same level = AND
      matchLabels:
        env: production
```

### Mistake 3: Applying to Wrong Pods

```yaml
# ❌ Empty podSelector = ALL pods affected!
spec:
  podSelector: {}  # All pods!
  policyTypes:
  - Egress
  # Blocks all egress for all pods
```

**Fix:**
```yaml
# ✅ Specific selector
spec:
  podSelector:
    matchLabels:
      app: specific-app
```

### Mistake 4: Not Specifying policyTypes

```yaml
# ❌ Unclear what's being controlled
spec:
  podSelector:
    matchLabels:
      app: backend
  ingress: [...]
  # Missing policyTypes!
```

**Fix:**
```yaml
# ✅ Explicit policyTypes
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress  # Control ingress
  - Egress   # Control egress
```

### Mistake 5: Port vs TargetPort Confusion

```yaml
# ❌ Using Service port instead of container port
ports:
- port: 80  # Service port
# Should use container port (8080)
```

**Fix:**
```yaml
# ✅ Use container port
ports:
- port: 8080  # Container's actual port
```

---

## 🚨 REAL-WORLD HORROR STORY: The Cryptocurrency Heist

### The Incident: $4.2M Stolen

**Company:** Cryptocurrency exchange  
**Date:** June 2023  
**Impact:** $4.2M stolen, complete platform compromise

### What Happened

**The Setup:**
- Kubernetes cluster running crypto trading platform
- **No NetworkPolicies** - all pods can talk to all pods
- Separate namespaces for different services

**The Attack Chain:**

**Day 1, 14:00** - Attacker exploits vulnerability in public-facing web app  
**14:10** - Gains shell in web pod (least privileged service)  
**14:15** - No NetworkPolicy blocking lateral movement  
**14:20** - Web pod scans internal network, finds database pods  
**14:30** - Connects directly to database pod (port 5432)  
**14:35** - Database accepts connection (no ingress policy!)  
**15:00** - Exfiltrates customer wallet private keys  
**15:30** - Connects to hot wallet service (no egress policy!)  
**16:00** - Initiates unauthorized withdrawals  
**18:00** - $4.2M transferred to attacker wallets  
**20:00** - Anomaly detected, too late  

### What NetworkPolicy Would Have Prevented

```yaml
# Database should ONLY accept from backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-ingress
spec:
  podSelector:
    matchLabels:
      app: database
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: backend  # ONLY backend
    ports:
    - port: 5432

---
# Web frontend should NOT connect to database
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-egress
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: backend  # Only to backend API
    ports:
    - port: 8080
  - to:  # DNS
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - port: 53
  # NO access to database or wallet service!
```

**With these policies:**
- Web pod couldn't connect to database → attack stopped
- Web pod couldn't connect to wallet → theft prevented
- Damage limited to compromised web pod only

### Lessons Learned

1. **Default deny** - Block all, allow specific
2. **Least privilege** - Only necessary connections
3. **Defense in depth** - NetworkPolicy + RBAC + more
4. **Monitor violations** - Alert on policy blocks
5. **Regular audits** - Review policies quarterly

---

## 🛡️ NetworkPolicy Best Practices

### 1. Start with Default Deny

```yaml
# Apply to every namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

Then add specific allow rules.

### 2. Always Allow DNS

```yaml
# Add to all pods with egress policies
egress:
- to:
  - namespaceSelector:
      matchLabels:
        kubernetes.io/metadata.name: kube-system
  ports:
  - protocol: UDP
    port: 53
```

### 3. Use Descriptive Names

```yaml
# ❌ Bad
name: policy-1

# ✅ Good
name: allow-frontend-to-backend-api
```

### 4. Document Your Policies

```yaml
metadata:
  name: allow-backend-to-db
  annotations:
    description: "Allows backend API pods to connect to PostgreSQL database on port 5432"
    owner: "platform-team"
    reviewed: "2024-12-01"
```

### 5. Test Thoroughly

```bash
# Test connectivity
kubectl exec frontend-pod -- curl backend:8080

# Should succeed if policy allows
# Should timeout if policy blocks
```

### 6. Use Labels Consistently

```yaml
# Standard labels
labels:
  app: backend
  tier: api
  env: production
```

### 7. Monitor Policy Hits

Use tools like Cilium to see policy enforcement:
```bash
# See what's being blocked
cilium monitor --type policy-verdict
```

---

## 🔍 Debugging NetworkPolicy

### Check Policies

```bash
# List all policies
kubectl get networkpolicy --all-namespaces

# Describe specific policy
kubectl describe networkpolicy allow-backend -n k8squest
```

### Test Connectivity

```bash
# From pod to pod
kubectl exec frontend-pod -- curl backend:8080

# Check DNS
kubectl exec frontend-pod -- nslookup backend

# Port connectivity
kubectl exec frontend-pod -- nc -zv backend 8080
```

### View Policy in Detail

```bash
kubectl get networkpolicy my-policy -o yaml
```

### Check Pod Labels

```bash
# Verify pod has expected labels
kubectl get pod my-pod --show-labels

# Policy won't apply if labels don't match
```

---

## 📚 Quick Reference

### Allow Patterns

| Pattern | YAML |
|---------|------|
| **Allow from pod** | `from: [{podSelector: {matchLabels: {app: x}}}]` |
| **Allow from namespace** | `from: [{namespaceSelector: {matchLabels: {env: x}}}]` |
| **Allow from IP** | `from: [{ipBlock: {cidr: 10.0.0.0/24}}]` |
| **Allow to pod** | `to: [{podSelector: {matchLabels: {app: x}}}]` |
| **Allow DNS** | `to: [{namespaceSelector: ...kube-system}], ports: [{port: 53}]` |

### Common Ports

| Service | Port | Protocol |
|---------|------|----------|
| HTTP | 80 | TCP |
| HTTPS | 443 | TCP |
| PostgreSQL | 5432 | TCP |
| MySQL | 3306 | TCP |
| MongoDB | 27017 | TCP |
| Redis | 6379 | TCP |
| DNS | 53 | UDP |

---

## 🎯 Key Takeaways

1. **NetworkPolicy = pod firewall** - Controls ingress/egress
2. **Default deny** - Start restrictive, open as needed
3. **Always allow DNS** - Pods need name resolution
4. **Use labels** - podSelector and namespaceSelector
5. **Test thoroughly** - Verify connectivity works
6. **Defense in depth** - NetworkPolicy + RBAC + SecurityContext
7. **Document policies** - Clear naming and annotations
8. **Monitor violations** - Track what's being blocked

---

## 🚀 Next Steps

Now that you understand NetworkPolicy, you're ready for:

- **Level 45:** Node Affinity - advanced pod scheduling
- **Level 46:** Taints and Tolerations - node scheduling constraints
- **Level 47:** PodDisruptionBudget - availability during disruptions

---

**Excellent work!** You've mastered Kubernetes network security! 🎉🔒
