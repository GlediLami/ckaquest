# 🎓 Level 23 Debrief: DNS Resolution in Kubernetes

## What Just Happened?

You fixed a **DNS resolution failure** where a pod couldn't connect to a service because it was using the wrong hostname!

This is one of the most common issues in Kubernetes - assuming service names match what you think they are, instead of checking what they actually are.

DNS in Kubernetes is automatic, but you need to use the CORRECT service name!

---

## 🧠 The Mental Model: Kubernetes DNS

### How Kubernetes DNS Works:

Every service gets automatic DNS records:

```
<service-name>.<namespace>.svc.cluster.local
```

**Examples:**
```
database-service.ckaquest.svc.cluster.local  # Full FQDN
database-service.ckaquest                    # Shortened
database-service                             # Same namespace only
```

### DNS Resolution Flow:

```
1. Pod makes request to "database-service"
   ↓
2. CoreDNS receives query
   ↓
3. Searches: <name>.<current-namespace>.svc.cluster.local
   ↓
4. Returns ClusterIP of service
   ↓
5. Pod connects to ClusterIP
   ↓
6. kube-proxy routes to pod
```

---

## 🔍 Common DNS Patterns

### Pattern 1: Same Namespace (Short Name)
```yaml
# Service in namespace: ckaquest
apiVersion: v1
kind: Service
metadata:
  name: database-service
  namespace: ckaquest

# Pod in same namespace can use:
- h database-service  # ✅ Works!
```

### Pattern 2: Different Namespace (FQDN)
```yaml
# Service in namespace: production
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: production

# Pod in namespace: staging needs:
- h api-service.production  # ✅ Works!
- h api-service.production.svc.cluster.local  # ✅ Also works!
- h api-service  # ❌ Fails! (looks in staging namespace)
```

### Pattern 3: External Services
```yaml
# For external databases/APIs:
- h database.example.com  # ✅ Normal DNS resolution
```

---

## 🚨 Real-World Incident: The Case-Sensitive Catastrophe

### Company: Financial Services Platform (2021)
**Impact:** 6-hour outage, $200K revenue loss

**What Happened:**
- Team deployed microservices with naming convention
- Service: "PaymentProcessor" (camelCase)
- Client code used: "paymentprocessor" (lowercase)
- Kubernetes service names are case-sensitive!
- **DNS lookups failed silently**
- Payments stopped processing

**Timeline:**
- 9:00 AM - Deployment completed successfully
- 9:15 AM - First payment failures
- 10:00 AM - Customer complaints escalate
- 11:00 AM - Engineers check pod logs (connection timeouts)
- 12:00 PM - Check service (exists and healthy!)
- 1:00 PM - Finally check DNS: `nslookup paymentprocessor` → not found
- 2:00 PM - Realize case mismatch
- 3:00 PM - Fixed and redeployed

**The Fix:**
```yaml
# Wrong approach:
metadata:
  name: PaymentProcessor  # CamelCase

# Correct approach:
metadata:
  name: payment-processor  # kebab-case (Kubernetes convention)
```

**Lesson:** Use lowercase with hyphens for all Kubernetes resource names!

---

## 💡 DNS Troubleshooting Techniques

### Test 1: Check Service Exists
```bash
kubectl get svc -n ckaquest
# Verify service name exactly
```

### Test 2: DNS Resolution from Pod
```bash
kubectl exec -it app-client -n ckaquest -- nslookup database-service

# Expected output:
# Server: 10.96.0.10
# Address: 10.96.0.10:53
# 
# Name: database-service.ckaquest.svc.cluster.local
# Address: 10.100.200.50
```

### Test 3: Full FQDN
```bash
kubectl exec -it app-client -n ckaquest -- \
  nslookup database-service.ckaquest.svc.cluster.local
```

### Test 4: Check CoreDNS
```bash
kubectl get pods -n kube-system | grep coredns
# Should show running CoreDNS pods
```

### Test 5: Connectivity Test
```bash
kubectl exec -it app-client -n ckaquest -- \
  curl http://database-service:5432
```

---

## 🎯 Kubernetes DNS Best Practices

### 1. Use Lowercase Kebab-Case
```yaml
# Good:
name: my-service
name: api-gateway
name: database-primary

# Bad:
name: MyService
name: API_Gateway
name: databasePrimary
```

### 2. Descriptive Service Names
```yaml
# Good:
name: user-authentication-service
name: payment-processor-api
name: database-postgresql

# Bad:
name: svc1
name: api
name: db
```

### 3. Document DNS Names
```yaml
metadata:
  name: payment-api
  annotations:
    dns-name: "payment-api.production.svc.cluster.local"
    short-name: "payment-api (same namespace only)"
```

### 4. Use Environment Variables
```yaml
# Instead of hardcoding:
command: ["curl", "http://api-service:8080"]

# Use env vars:
env:
- name: API_SERVICE_HOST
  value: api-service
- name: API_SERVICE_PORT
  value: "8080"
command: ["curl", "http://$(API_SERVICE_HOST):$(API_SERVICE_PORT)"]
```

### 5. Test DNS During Development
```yaml
# Add a debug container:
- name: debug
  image: busybox
  command: ["sleep", "3600"]
  
# Then test DNS:
kubectl exec debug -- nslookup my-service
```

---

## 📊 DNS Record Types in Kubernetes

### Service ClusterIP Record:
```
database-service.ckaquest.svc.cluster.local → 10.100.200.50 (ClusterIP)
```

### Headless Service Records (clusterIP: None):
```
database-service.ckaquest.svc.cluster.local → 10.244.1.5 (Pod 1)
                                            → 10.244.2.8 (Pod 2)
                                            → 10.244.3.2 (Pod 3)
```

### Pod Records (StatefulSet):
```
pod-0.database-service.ckaquest.svc.cluster.local → 10.244.1.5
pod-1.database-service.ckaquest.svc.cluster.local → 10.244.2.8
```

---

## 💼 Interview Questions You Can Now Answer

**Q: "How does Kubernetes DNS work?"**

**A:** "CoreDNS runs in kube-system namespace and provides DNS for the cluster. Services get automatic A records in format `<service>.<namespace>.svc.cluster.local`. Pods can use short names within the same namespace, or FQDNs for cross-namespace communication."

**Q: "A pod can't connect to a service. How do you debug?"**

**A:** "First, verify the service name with `kubectl get svc`. Then test DNS resolution from the pod with `nslookup <service-name>`. Check if CoreDNS is running in kube-system. Verify the pod is using the correct service name - it's case-sensitive!"

**Q: "What's the difference between short names and FQDNs?"**

**A:** "Short names (e.g., `my-service`) only work within the same namespace. FQDNs (e.g., `my-service.production.svc.cluster.local`) work across namespaces. Short names are convenient but FQDNs are explicit and clearer."

---

## 🎓 What You Learned

✅ **Kubernetes DNS format** - `<service>.<namespace>.svc.cluster.local`  
✅ **Short names vs FQDNs** - When to use each  
✅ **DNS troubleshooting** - nslookup, service verification  
✅ **Common mistakes** - Case sensitivity, wrong names  
✅ **CoreDNS role** - Automatic DNS for services  

---

## 🚀 Next Steps

- Explore headless services (upcoming level)
- Learn about StatefulSet DNS records
- Understand cross-namespace service discovery
- Practice with ExternalName services

---

**Remember:** Service names are case-sensitive and must match exactly. When in doubt, `kubectl get svc` is your friend!

🎉 **Congratulations on mastering Kubernetes DNS!**

## Exam angle

Service DNS name: <svc>.<ns>.svc.cluster.local. Test from inside:

```bash
k run t --rm -it --image=busybox -- nslookup database-service
```

Bookmark: https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/

Your notes: DNS in Kubernetes
