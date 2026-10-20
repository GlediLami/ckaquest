# 🎓 Mission Debrief: HPA Can't Scale

## What Happened

Your HorizontalPodAutoscaler (HPA) was configured correctly, but it couldn't scale because **metrics-server was not installed**.

Without metrics-server, Kubernetes has no way to know the CPU/memory usage of pods, so HPA can't make scaling decisions.

This is one of the most common HPA issues in new clusters!

## How Kubernetes Behaved

**HPA dependency chain**:

```
HPA wants to scale
    ↓
Needs current CPU/memory metrics
    ↓
Queries Metrics API
    ↓
Metrics API served by metrics-server
    ↓
❌ metrics-server not installed
    ↓
HPA shows "<unknown>/50%"
    ↓
Cannot make scaling decisions
```

**What metrics-server does**:

```
metrics-server runs as a deployment in kube-system namespace
    ↓
Collects resource metrics from kubelet on each node
    ↓
Aggregates metrics (CPU, memory usage)
    ↓
Exposes them via Kubernetes Metrics API
    ↓
HPA, kubectl top, and other tools consume these metrics
```

## The Correct Mental Model

### Kubernetes Metrics Architecture

```
┌─────────────────────────────────────────────────┐
│                  kubectl top                     │
│                      HPA                         │
│            Dashboard / Monitoring                │
└────────────────────┬────────────────────────────┘
                     │ Query metrics
                     ↓
         ┌───────────────────────┐
         │    Metrics API        │
         │ (metrics.k8s.io/v1)   │
         └──────────┬────────────┘
                    │ Implemented by
                    ↓
         ┌───────────────────────┐
         │   metrics-server      │
         │  (kube-system ns)     │
         └──────────┬────────────┘
                    │ Scrapes metrics
                    ↓
    ┌───────────────────────────────────┐
    │  kubelet on each node             │
    │  (cAdvisor provides container     │
    │   CPU/memory stats)                │
    └───────────────────────────────────┘
```

### HPA Scaling Logic

```yaml
# HPA configuration
spec:
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50  # Target: 50% CPU
```

**How HPA decides to scale**:

```
Current state:
- Deployment has 2 pods
- Pod 1: 80% CPU
- Pod 2: 70% CPU
- Average: 75% CPU

Target: 50% CPU

HPA calculation:
  desiredReplicas = ceil(currentReplicas × (currentMetric / targetMetric))
  desiredReplicas = ceil(2 × (75 / 50))
  desiredReplicas = ceil(2 × 1.5)
  desiredReplicas = ceil(3)
  desiredReplicas = 3

Action: Scale up from 2 to 3 replicas
```

**Scaling behavior**:

- **Scale up**: Immediate (when CPU > target)
- **Scale down**: 5-minute stabilization window (prevent flapping)
- **Cooldown**: 3 minutes between scale-up events, 5 minutes for scale-down

### metrics-server Configuration

**Standard installation**:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**For local development (kind, Docker Desktop, minikube)**:

```bash
# Add --kubelet-insecure-tls flag
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```

Why `--kubelet-insecure-tls`?
- Production clusters have proper TLS certificates
- Local clusters often use self-signed certs
- metrics-server can't verify them without this flag
- **Only use in development, never in production!**

## Real-World Incident Example

**Company**: Mobile gaming company (10M daily active users)  
**Impact**: 2-hour outage during product launch, 100% traffic loss  
**Cost**: $3.5M in lost revenue + $2M in refunds  

**What happened**:

The team prepared for a big game launch with 10x expected traffic. They configured HPA to handle the load:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: game-server-hpa
spec:
  scaleTargetRef:
    kind: Deployment
    name: game-server
  minReplicas: 10
  maxReplicas: 500
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

They tested in staging (which had metrics-server installed). Everything worked perfectly!

**The failure** (Launch day):

```
10:00 - Game launches
10:00 - Traffic starts ramping up (50K → 100K → 200K users/min)
10:05 - CPU on 10 pods hits 90%
10:05 - HPA should scale to 13 pods... but doesn't
10:08 - CPU hits 100%, pods start crashing
10:10 - All 10 pods restarting in loop
10:10 - Game completely down
10:10 - Team paged urgently
10:15 - Check HPA: "unable to get metrics for resource cpu"
10:20 - Check metrics-server: NOT FOUND
10:20 - Realize: Production cluster doesn't have metrics-server!
10:25 - Start installing metrics-server
10:30 - metrics-server running
10:35 - HPA starts working
10:40 - Scales to 180 pods
10:50 - Service stabilizes
12:00 - Fully recovered (2 hours of downtime)
```

**Root cause**:
- **Infrastructure as Code not enforced** - Staging had metrics-server, prod didn't
- **No deployment checklist** - Nobody verified metrics-server existed
- **Testing in wrong environment** - Staging ≠ production
- **No monitoring** - No alert for "HPA unable to scale"

**The fix implemented**:

1. **Terraform module for cluster setup**:
```hcl
resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  namespace  = "kube-system"
}
```

2. **Pre-deployment validation**:
```bash
# Check metrics-server before allowing deployments
if ! kubectl top nodes &>/dev/null; then
    echo "ERROR: metrics-server not working"
    exit 1
fi
```

3. **HPA monitoring**:
```yaml
# Alert if HPA can't get metrics for 2 minutes
- alert: HPAMetricsUnavailable
  expr: kube_horizontalpodautoscaler_status_condition{condition="ScalingActive",status="false"} == 1
  for: 2m
```

**Lessons learned**:
1. **Verify dependencies exist** before deploying features that need them
2. **Staging must match production** infrastructure
3. **Monitor HPA health** - alert on scaling failures
4. **Load test with actual scaling** - not just fixed pod count

## Commands You Mastered

```bash
# Check HPA status
kubectl get hpa -n <namespace>
# Look at TARGETS - should show "X%/50%", not "<unknown>/50%"

# Describe HPA (see detailed status)
kubectl describe hpa <name> -n <namespace>

# Check if metrics-server is installed
kubectl get deployment metrics-server -n kube-system

# Install metrics-server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# For local clusters, add insecure TLS flag
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'

# Wait for metrics-server to be ready
kubectl wait --for=condition=available --timeout=60s deployment/metrics-server -n kube-system

# Test if metrics work
kubectl top nodes           # Node CPU/memory
kubectl top pods -n <ns>    # Pod CPU/memory

# Watch HPA scale in real-time
kubectl get hpa -n <namespace> -w

# Generate load to trigger scaling (testing)
kubectl run -it --rm load-generator --image=busybox --restart=Never -- /bin/sh -c "while true; do wget -q -O- http://service-name; done"
```

## Best Practices for HPA

### ✅ DO:

1. **Always install metrics-server**:
   ```bash
   # Include in cluster setup automation
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```

2. **Set resource requests** (HPA needs them):
   ```yaml
   resources:
     requests:
       cpu: 200m      # HPA uses this as baseline
       memory: 256Mi
     limits:
       cpu: 500m
       memory: 512Mi
   ```

3. **Use reasonable target utilization**:
   ```yaml
   # Good: 50-70% target (room for spikes)
   averageUtilization: 60
   
   # Bad: 90% target (no headroom for bursts)
   averageUtilization: 90
   ```

4. **Set min/max replicas appropriately**:
   ```yaml
   minReplicas: 2   # Always some redundancy
   maxReplicas: 10  # Reasonable ceiling
   ```

5. **Monitor HPA health**:
   ```yaml
   # Alert if HPA can't scale
   - alert: HPAUnableToScale
     expr: kube_horizontalpodautoscaler_status_condition{condition="AbleToScale",status="false"} == 1
   ```

### ❌ DON'T:

1. **Don't forget resource requests**:
   ```yaml
   # Bad: No requests = HPA can't calculate percentage
   spec:
     containers:
     - name: app
       image: myapp
   
   # Good: Requests defined
   spec:
     containers:
     - name: app
       image: myapp
       resources:
         requests:
           cpu: 100m
   ```

2. **Don't use HPA with Deployment that has no requests**:
   ```yaml
   # This won't work!
   spec:
     containers:
     - name: app
       resources: {}  # No requests = HPA fails
   ```

3. **Don't set minReplicas: 1 for critical services**:
   ```yaml
   # Bad: Single point of failure
   minReplicas: 1
   
   # Good: Always have redundancy
   minReplicas: 2
   ```

4. **Don't use very aggressive scaling**:
   ```yaml
   # Bad: Scales at slightest load
   averageUtilization: 30
   
   # Good: Balanced
   averageUtilization: 60
   ```

## Advanced HPA Configurations

### Multi-metric HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: multi-metric-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  # Scale on CPU
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  # AND memory
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  # AND custom metric (requires custom metrics adapter)
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
```

### Behavior Configuration (Kubernetes 1.18+)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 5 min stabilization
      policies:
      - type: Percent
        value: 50         # Max 50% scale down at once
        periodSeconds: 60
      - type: Pods
        value: 2          # Max 2 pods removed per minute
        periodSeconds: 60
      selectPolicy: Min   # Use most conservative policy
    scaleUp:
      stabilizationWindowSeconds: 0  # Immediate scale up
      policies:
      - type: Percent
        value: 100        # Can double pod count
        periodSeconds: 15
      - type: Pods
        value: 4          # Max 4 pods added per 15s
        periodSeconds: 15
      selectPolicy: Max   # Use most aggressive policy
```

## What's Next?

You've learned how to configure HPA and install the required metrics-server dependency.

Next level: Rollout strategies! You'll learn how misconfigured rolling update parameters can cause downtime.

**Key takeaway**: HPA requires metrics-server. Always verify it's installed and working before deploying HPAs to production!
