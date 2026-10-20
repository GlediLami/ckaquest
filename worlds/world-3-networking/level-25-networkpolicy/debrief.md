# Level 25: NetworkPolicy Too Restrictive - Mission Debrief

## Mission Overview

**Objective:** Fix an overly restrictive NetworkPolicy that was blocking legitimate traffic between frontend and backend pods.

**XP Awarded:** 250 XP  
**Difficulty:** Intermediate  
**Concepts:** Kubernetes NetworkPolicy, Pod-to-pod Communication, Label Selectors, Ingress Rules

---

## What You Encountered

You deployed a frontend application that needed to communicate with a backend API. Both pods were running, the service was configured correctly, and endpoints existed. Yet the frontend couldn't reach the backend—all connection attempts timed out.

The culprit? A NetworkPolicy with an incorrect label selector that was blocking all traffic from the frontend.

**The Broken Configuration:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
spec:
  podSelector:
    matchLabels:
      app: backend        # Applies to backend pods
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: admin-tool  # ❌ WRONG! Only allows "admin-tool" pods
    ports:
    - protocol: TCP
      port: 8080
```

**The Problem:**
- Frontend pod has label: `app: frontend`
- NetworkPolicy allows traffic from: `app: admin-tool`
- Match? NO! → All frontend traffic DENIED
- Result: Connection timeouts

---

## The Root Cause: Label Selector Mismatch

### Understanding NetworkPolicy

NetworkPolicy is Kubernetes' firewall for pod-to-pod traffic. It uses label selectors to control which pods can communicate with each other.

**Three Key Components:**

1. **podSelector** - WHO the policy applies TO (target pods)
2. **policyTypes** - What types of traffic to control (Ingress, Egress, or both)
3. **ingress/egress rules** - WHO can send traffic and WHAT ports

```yaml
spec:
  podSelector:           # TARGET: Apply to these pods
    matchLabels:
      app: backend
  
  policyTypes:          # DIRECTION: Control incoming traffic
  - Ingress
  
  ingress:              # RULES: Allow traffic from these sources
  - from:
    - podSelector:
        matchLabels:
          app: frontend  # SOURCE: Pods that can send traffic
    ports:
    - protocol: TCP
      port: 8080        # PORT: Only this port allowed
```

**How It Works:**

```
┌─────────────────────┐
│ Frontend Pod        │
│ Labels:             │
│   app: frontend ────┼────┐
│   tier: web         │    │
└─────────────────────┘    │
                           │
                           ▼
                    ┌──────────────────────────┐
                    │ NetworkPolicy Check      │
                    │ Does label "app:         │
                    │ frontend" match ingress  │
                    │ podSelector?             │
                    └──────────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
               YES                   NO
                │                     │
                ▼                     ▼
         ┌──────────────┐      ┌──────────────┐
         │ ALLOW        │      │ DENY         │
         │ Traffic      │      │ Connection   │
         │ Passes ✅    │      │ Timeout ❌   │
         └──────────────┘      └──────────────┘
                │                     
                ▼                     
       ┌─────────────────────┐
       │ Backend Pod         │
       │ Labels:             │
       │   app: backend      │
       │   tier: api         │
       └─────────────────────┘
```

### Default Deny Behavior

**CRITICAL:** Once you create a NetworkPolicy for a pod, that pod becomes "protected" and ALL traffic is denied by default EXCEPT what you explicitly allow.

```yaml
# NO NetworkPolicy
# Result: All traffic allowed (open)

# NetworkPolicy with empty ingress
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress: []  # Empty = deny all ingress

# Result: ALL incoming traffic denied!
```

This is why getting the label selector wrong is so dangerous—you accidentally deny legitimate traffic!

---

## The Fix Explained

**What You Changed:**

```yaml
# BEFORE (broken)
ingress:
- from:
  - podSelector:
      matchLabels:
        app: admin-tool    # Wrong label

# AFTER (solution)
ingress:
- from:
  - podSelector:
      matchLabels:
        app: frontend      # Correct label
```

**Why This Works:**

1. **Frontend pod** has label `app: frontend`
2. **NetworkPolicy** now allows traffic from pods with `app: frontend`
3. **Match:** YES ✅
4. **Result:** Frontend can connect to backend

The NetworkPolicy now correctly identifies the frontend as an authorized source and allows its traffic to reach the backend on port 8080.

---

## Real-World Incident: The Midnight Lockout

**Company:** Financial services platform (payment processing)  
**Date:** November 2021  
**Impact:** 4 hours of downtime, 50,000 failed transactions, $2.3M in lost revenue  

### What Happened

The security team decided to implement NetworkPolicies across all production namespaces to improve security posture. They created policies to restrict database access to only authorized applications.

**The Broken NetworkPolicy:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: postgres-access-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: backend       # ❌ Used "tier" instead of "app"
    ports:
    - protocol: TCP
      port: 5432
```

**The Application Labels:**
```yaml
# Payment service (needs database access)
metadata:
  labels:
    app: payment-service
    team: payments
    
# User service (needs database access)
metadata:
  labels:
    app: user-service
    team: identity
```

### The Problem

The NetworkPolicy used label selector `tier: backend`, but NONE of the application pods had that label! They used `app: payment-service`, `app: user-service`, etc.

**Result:**
- ALL application pods were denied database access
- Every query timed out
- Payment processing completely stopped
- User authentication failed
- Website became unusable

### Timeline

**11:00 PM:** Security team deployed NetworkPolicies to production  
**11:05 PM:** Payment API started returning 500 errors  
**11:10 PM:** All database-dependent services failed  
**11:15 PM:** On-call engineer paged (monitoring detected massive error spike)  
**11:30 PM:** Team identified database connection timeouts  
**11:45 PM:** Suspected network issue, checked firewall rules (nothing wrong)  
**12:15 AM:** Checked NetworkPolicies, found label mismatch  
**12:30 AM:** Hotfix deployed with correct labels  
**1:00 AM:** Services restored, transactions processing again  
**3:00 AM:** Full validation complete  

### The Hotfix

**Option 1: Fix the NetworkPolicy**
```yaml
ingress:
- from:
  - podSelector:
      matchLabels:
        app: payment-service
  - podSelector:
      matchLabels:
        app: user-service
  # ... list all authorized services
```

**Option 2: Use a common label** (better approach)
```yaml
# Add consistent labels to all backend services
metadata:
  labels:
    app: payment-service
    tier: backend          # ✅ Add this to all backend pods

# NetworkPolicy can now use it
ingress:
- from:
  - podSelector:
      matchLabels:
        tier: backend      # ✅ Now matches!
```

**Option 3: Use namespace selector** (if all services in same namespace)
```yaml
ingress:
- from:
  - namespaceSelector:
      matchLabels:
        name: backend-services
```

### Lessons Learned

1. **Test NetworkPolicies in Staging:**
   - Never deploy NetworkPolicies directly to production
   - Test in staging with identical labels and traffic patterns
   - Verify connectivity before promoting to production

2. **Use Consistent Labeling:**
   - Establish label conventions across organization
   - Document required labels for NetworkPolicy access
   - Automate label validation in CI/CD

3. **Monitor Denied Connections:**
   - Log NetworkPolicy denials
   - Alert on unexpected connection failures
   - Track denied connections by source/destination

4. **Gradual Rollout:**
   - Deploy NetworkPolicies namespace-by-namespace
   - Start with logging-only mode (if controller supports)
   - Have instant rollback plan

5. **Documentation:**
   - Document which services need to communicate
   - Maintain service dependency maps
   - Include NetworkPolicy requirements in service documentation

---

## NetworkPolicy Deep Dive

### 1. Ingress vs Egress

**Ingress:** INCOMING traffic TO the protected pod
```yaml
policyTypes:
- Ingress        # Controls traffic coming IN

ingress:
- from:          # WHO can send traffic TO me
  - podSelector:
      matchLabels:
        app: frontend
```

**Egress:** OUTGOING traffic FROM the protected pod
```yaml
policyTypes:
- Egress         # Controls traffic going OUT

egress:
- to:            # WHERE can I send traffic TO
  - podSelector:
      matchLabels:
        app: database
```

**Both:**
```yaml
policyTypes:
- Ingress
- Egress

ingress:
- from:
  - podSelector:
      matchLabels:
        app: frontend

egress:
- to:
  - podSelector:
      matchLabels:
        app: database
```

### 2. Multiple Selectors (OR Logic)

```yaml
ingress:
- from:
  - podSelector:
      matchLabels:
        app: frontend
  - podSelector:
      matchLabels:
        app: admin
```

**Meaning:** Allow traffic from pods with `app: frontend` OR `app: admin`

### 3. Combined Selectors (AND Logic)

```yaml
ingress:
- from:
  - podSelector:
      matchLabels:
        app: frontend
    namespaceSelector:
      matchLabels:
        env: production
```

**Meaning:** Allow traffic from pods with `app: frontend` AND in namespace labeled `env: production`

### 4. Namespace Selectors

```yaml
ingress:
- from:
  - namespaceSelector:
      matchLabels:
        team: backend
```

**Meaning:** Allow traffic from ANY pod in namespaces labeled `team: backend`

### 5. IP Block Selectors

```yaml
ingress:
- from:
  - ipBlock:
      cidr: 10.0.0.0/24
      except:
      - 10.0.0.1/32  # Except this specific IP
```

**Meaning:** Allow traffic from IP range 10.0.0.0/24 except 10.0.0.1

### 6. Port Restrictions

```yaml
ingress:
- from:
  - podSelector:
      matchLabels:
        app: frontend
  ports:
  - protocol: TCP
    port: 8080    # Only allow port 8080
  - protocol: TCP
    port: 9090    # Also allow port 9090
```

### 7. Default Deny All

```yaml
# Deny all ingress traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}    # Applies to ALL pods
  policyTypes:
  - Ingress
  # No ingress rules = deny all
```

```yaml
# Deny all egress traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-egress
spec:
  podSelector: {}    # Applies to ALL pods
  policyTypes:
  - Egress
  # No egress rules = deny all
```

### 8. Allow All

```yaml
# Allow all ingress traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-all-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - {}              # Empty rule = allow all
```

---

## Common NetworkPolicy Patterns

### Pattern 1: Frontend → Backend → Database

```yaml
# Allow frontend to access backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
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
    - protocol: TCP
      port: 8080
---
# Allow backend to access database
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-policy
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
    - protocol: TCP
      port: 5432
```

### Pattern 2: Allow Ingress Controller

```yaml
# Allow ingress controller to access all services
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-controller
spec:
  podSelector:
    matchLabels:
      exposed: "true"    # Only pods with this label
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
      podSelector:
        matchLabels:
          app: ingress-nginx
```

### Pattern 3: Allow Monitoring/Metrics

```yaml
# Allow Prometheus to scrape metrics
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-prometheus
spec:
  podSelector: {}        # All pods
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
      podSelector:
        matchLabels:
          app: prometheus
    ports:
    - protocol: TCP
      port: 9090       # Metrics port
```

### Pattern 4: Allow DNS

```yaml
# Allow all pods to query DNS
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
          name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

### Pattern 5: Cross-namespace Communication

```yaml
# Allow frontend in "app" namespace to access backend in "services" namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-cross-namespace
  namespace: services
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: app
      podSelector:
        matchLabels:
          app: frontend
```

---

## Debugging NetworkPolicy Issues

### 1. Check if NetworkPolicy Exists

```bash
# List all NetworkPolicies in namespace
kubectl get networkpolicy -n k8squest

# Describe specific NetworkPolicy
kubectl describe networkpolicy backend-network-policy -n k8squest
```

Look for:
- **podSelector:** Which pods does it apply to?
- **Allowing ingress traffic:** What's allowed?
- **Allowing egress traffic:** Where can traffic go?

### 2. Check Pod Labels

```bash
# View pod labels
kubectl get pod frontend -n k8squest --show-labels

# Check if labels match NetworkPolicy selector
kubectl get pod -n k8squest -l app=frontend
```

If no pods match the NetworkPolicy selector, it's not being applied!

### 3. Test Connectivity

```bash
# Try to connect from frontend to backend
kubectl exec frontend -n k8squest -- wget -q -O- http://backend-service:8080 --timeout=5

# Success: Prints response
# Failure: Timeout or connection refused
```

### 4. Check NetworkPolicy Controller Logs

```bash
# Find NetworkPolicy controller pods (depends on CNI)
# For Calico:
kubectl logs -n kube-system -l k8s-app=calico-node

# For Cilium:
kubectl logs -n kube-system -l k8s-app=cilium

# For Weave:
kubectl logs -n kube-system -l name=weave-net
```

Look for denied connection logs.

### 5. Verify CNI Plugin Supports NetworkPolicy

Not all CNI plugins support NetworkPolicy!

**Support NetworkPolicy:**
- Calico ✅
- Cilium ✅
- Weave Net ✅
- Kube-router ✅

**DO NOT Support:**
- Flannel ❌ (without additional setup)
- Basic kubenet ❌

Check your CNI:
```bash
kubectl get pods -n kube-system
```

### 6. Test with curl Pod

Create a test pod to diagnose connectivity:

```bash
# Create test pod
kubectl run test -n k8squest --image=nicolaka/netshoot -- sleep 3600

# Test connection
kubectl exec test -n k8squest -- curl http://backend-service:8080

# Check if NetworkPolicy affects test pod
kubectl label pod test -n k8squest app=frontend

# Try again (should work if NetworkPolicy allows app=frontend)
kubectl exec test -n k8squest -- curl http://backend-service:8080
```

### 7. Temporarily Remove NetworkPolicy

```bash
# Delete NetworkPolicy to test if it's the issue
kubectl delete networkpolicy backend-network-policy -n k8squest

# Test connection (should work now)
kubectl exec frontend -n k8squest -- wget -q -O- http://backend-service:8080

# If it works now, NetworkPolicy was the problem
# Reapply with correct configuration
```

---

## Best Practices

### 1. Start Permissive, Then Tighten

```bash
# Phase 1: No NetworkPolicy (allow all)
# Deploy application, verify it works

# Phase 2: Default deny with broad allow
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
spec:
  podSelector:
    matchLabels:
      tier: backend
  ingress:
  - from:
    - podSelector: {}  # Allow from all pods in namespace

# Phase 3: Restrict to specific sources
ingress:
- from:
  - podSelector:
      matchLabels:
        tier: frontend  # Only frontend tier
```

### 2. Use Consistent Labels

```yaml
# Establish labeling conventions
metadata:
  labels:
    app: payment-service      # Application name
    tier: backend             # Architectural tier
    team: payments            # Owning team
    env: production           # Environment
```

Use these labels consistently in NetworkPolicies.

### 3. Document Service Dependencies

```yaml
# backend-deployment.yaml
metadata:
  annotations:
    dependencies: "database-service, cache-service"
    networkpolicy: "Allows ingress from tier=frontend on port 8080"
```

### 4. Test in Staging First

- Deploy NetworkPolicies to staging environment
- Run full integration tests
- Monitor for connection failures
- Only promote to production after validation

### 5. Monitor Denied Connections

Set up monitoring for NetworkPolicy denials:

```bash
# Calico example: View denied connections
kubectl logs -n kube-system -l k8s-app=calico-node | grep "DENY"
```

Alert on unexpected denials.

### 6. Use Namespace Isolation

```yaml
# Deny all cross-namespace traffic by default
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-cross-namespace
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector: {}  # Only same namespace
  egress:
  - to:
    - podSelector: {}  # Only same namespace
```

Then explicitly allow cross-namespace where needed.

### 7. Keep It Simple

```yaml
# ❌ TOO COMPLEX - hard to understand and maintain
ingress:
- from:
  - podSelector:
      matchLabels:
        app: frontend
    namespaceSelector:
      matchLabels:
        env: production
  - ipBlock:
      cidr: 10.0.0.0/16
      except:
      - 10.0.1.0/24
  ports:
  - protocol: TCP
    port: 8080
  - protocol: TCP
    port: 9090
  - protocol: UDP
    port: 8080
```

```yaml
# ✅ SIMPLE - clear and maintainable
ingress:
- from:
  - podSelector:
      matchLabels:
        tier: frontend
  ports:
  - protocol: TCP
    port: 8080
```

---

## Key Takeaways

1. **NetworkPolicy Uses Labels:**
   - `podSelector` determines which pods the policy applies TO
   - `ingress.from.podSelector` determines which pods can send traffic (source)
   - Labels must match EXACTLY for traffic to be allowed

2. **Default Deny Behavior:**
   - Once a NetworkPolicy is applied, ALL traffic is denied except what's explicitly allowed
   - Empty ingress/egress rules mean DENY ALL

3. **Multiple NetworkPolicies Are Additive:**
   - If multiple NetworkPolicies match a pod, their rules are combined (OR logic)
   - You can have one policy for frontend access, another for monitoring

4. **Testing is Critical:**
   - Always test NetworkPolicies in staging first
   - Verify connectivity after applying
   - Have rollback plan ready

5. **Common Mistakes:**
   - Label mismatch (most common!)
   - Forgetting to allow DNS (egress to kube-dns)
   - Applying policy to wrong pods (podSelector mistake)
   - Using AND logic when you need OR
   - Not allowing ingress controller or monitoring

6. **Real-World Lessons:**
   - NetworkPolicy mistakes can cause complete outages
   - Test with same labels and traffic patterns as production
   - Monitor denied connections
   - Document service dependencies
   - Use consistent labeling conventions

---

## What's Next?

You've mastered NetworkPolicy fundamentals! You now understand:
- ✅ How NetworkPolicy controls pod-to-pod traffic
- ✅ Label selector matching for ingress/egress rules
- ✅ Default deny behavior
- ✅ Debugging connectivity issues caused by NetworkPolicies

In the next levels, you'll explore session affinity for stateful applications, cross-namespace service communication, and more advanced networking patterns.

**Continue your K8sQuest journey to unlock the next challenge!** 🚀

---

## Additional Resources

- [Kubernetes NetworkPolicy Documentation](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [NetworkPolicy Recipes](https://github.com/ahmetb/kubernetes-network-policy-recipes)
- [Calico NetworkPolicy](https://docs.projectcalico.org/security/kubernetes-network-policy)
- [Cilium NetworkPolicy](https://docs.cilium.io/en/stable/policy/)

---

**Mission Complete!** 🎉  
You've earned 250 XP and mastered Kubernetes NetworkPolicy!
