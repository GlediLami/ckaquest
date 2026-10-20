# 🎓 Mission Debrief: Port Mismatch Mayhem

## What Happened

Your Service was forwarding traffic to port 8080 on the container, but the NGINX container actually listens on port 80. Result: Every request hit a closed port and failed with "connection refused."

## How Kubernetes Behaved

When a request comes to a Service:
1. Client connects to Service IP:port (e.g., 10.96.0.1:80)
2. Service forwards to one of its endpoints
3. Traffic sent to Pod IP:targetPort (e.g., 10.244.0.5:8080)
4. Container must be listening on that port

Your service forwarded to port 8080, but NGINX was listening on port 80. Step 4 failed—**no process on port 8080**.

## The Correct Mental Model

**Three port concepts**:

```yaml
apiVersion: v1
kind: Service
spec:
  ports:
  - port: 80          # External: what clients connect to
    targetPort: 8080  # Internal: what port on the Pod
    nodePort: 30080   # (Optional) Port on node for NodePort services
```

**Matching ports**:
```yaml
# Container listens on port 8080
containerPort: 8080

# Service must forward to the same port
targetPort: 8080
```

**Common patterns**:

| Pattern | Container | Service Port | Service TargetPort |
|---------|-----------|--------------|-------------------|
| Simple match | 80 | 80 | 80 |
| Port mapping | 8080 | 80 | 8080 |
| Named port | 8080 (named "http") | 80 | "http" |

## Real-World Incident Example

**Company**: E-commerce site during Black Friday  
**Impact**: 30 minutes of checkout failures  
**Cost**: $2.1M in lost sales

**What happened**:
A developer changed the application from port 8080 to 9000 to avoid conflicts in their local environment. They updated the Dockerfile and containerPort but **forgot to update the Service's targetPort**.

During deployment, pods started fine. Service existed. Endpoints looked healthy. But every checkout request got "connection refused."

**Why it was hard to debug**:
- Service showed as "healthy" (it existed with endpoints)
- Pods showed as "Ready" (readiness probe was on a different endpoint)
- Load balancer health checks passed (they targeted a health endpoint on correct port)
- Only actual checkout traffic failed

**Discovery**:
```bash
# Tried to test directly
kubectl port-forward pod/checkout-xyz 8080:9000 -n production
# Worked! ← This revealed the port mismatch

kubectl describe service checkout -n production
# Showed targetPort: 8080 (old value)

kubectl get pod checkout-xyz -n production -o yaml | grep containerPort
# Showed containerPort: 9000 (new value)
```

**The fix**: Updated Service targetPort to 9000. Instant recovery.

**Lesson**: When changing application ports, update EVERYWHERE:
- Dockerfile
- containerPort in pod spec
- targetPort in service spec
- Health check configurations
- Monitoring configurations

## Commands You Mastered

```bash
# Check container ports
kubectl get pod <name> -n <namespace> -o yaml | grep -A 2 ports:
kubectl describe pod <name> -n <namespace> | grep Port

# Check service ports
kubectl get service <name> -n <namespace>
kubectl describe service <name> -n <namespace>
kubectl get service <name> -n <namespace> -o yaml | grep -A 3 ports:

# Test connectivity directly
kubectl port-forward pod/<name> 8080:80 -n <namespace>
kubectl port-forward service/<name> 8080:80 -n <namespace>

# Execute commands in container to test
kubectl exec -it <pod-name> -n <namespace> -- curl localhost:80
kubectl exec -it <pod-name> -n <namespace> -- netstat -tlnp
```

## Understanding Port Types

**containerPort**: Informational only! Doesn't actually open the port.
```yaml
# This just documents what port the container uses
ports:
- containerPort: 8080
```

**Service port**: What clients use to access the service
```yaml
# Clients connect to service-ip:80
ports:
- port: 80
```

**targetPort**: Where service forwards traffic
```yaml
# Service forwards to pod-ip:8080
ports:
- targetPort: 8080
```

**Named ports** (best practice):
```yaml
# In Pod
ports:
- name: http
  containerPort: 8080

# In Service  
ports:
- port: 80
  targetPort: http  # References the name, not number!
```

Benefits: Change the port number once (in pod), service automatically uses new value.

## Debugging Port Issues

Step-by-step debugging:

```bash
# 1. Is pod running?
kubectl get pod <name> -n <namespace>

# 2. What port is container listening on?
kubectl exec <pod> -n <namespace> -- netstat -tlnp
# Or check the manifest
kubectl get pod <pod> -n <namespace> -o yaml | grep containerPort

# 3. Does service have endpoints?
kubectl get endpoints <service> -n <namespace>

# 4. What port does service target?
kubectl get service <service> -n <namespace> -o yaml | grep targetPort

# 5. Test direct pod connectivity
kubectl port-forward pod/<name> 9999:<containerPort> -n <namespace>
curl localhost:9999

# 6. Test service connectivity
kubectl port-forward service/<name> 9999:<port> -n <namespace>
curl localhost:9999
```

## What's Next?

You've learned single-container pod basics. Next challenge introduces multi-container pods where a sidecar container crashes and affects the whole pod!
