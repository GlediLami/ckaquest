# 🎓 Mission Debrief: The Restart Loop

## What Happened

Your pods were stuck in a restart loop because the liveness probe was checking endpoint `/nonexistent-healthz` which returned 404 (Not Found). Kubernetes interpreted this as "pod is unhealthy" and kept restarting it, which of course failed the health check again immediately.

This is a classic configuration error that can cause cascading failures in production.

## How Kubernetes Behaved

**Liveness Probe Flow**:

```
1. Pod starts
2. Wait initialDelaySeconds (5 seconds)
3. Check liveness probe (HTTP GET /nonexistent-healthz:8080)
4. Get 404 response ❌
5. Increment failure count (1/2)
6. Wait periodSeconds (5 seconds)
7. Check again → 404 ❌
8. Increment failure count (2/2)
9. failureThreshold reached! → Kill pod
10. Restart pod
11. Repeat from step 1 → Infinite loop!
```

**Why Kubernetes kept restarting**:
- Liveness probes determine if a container is **alive and healthy**
- Failed liveness probe = "Container is dead or stuck, restart it"
- Kubernetes tries to "heal" by restarting
- But if the probe config is wrong, restarts don't help!

## The Correct Mental Model

**Liveness vs Readiness Probes**:

| Probe Type | Purpose | Action on Failure | Use Case |
|------------|---------|-------------------|----------|
| **Liveness** | Is container alive? | Restart container | Detect deadlocks, infinite loops |
| **Readiness** | Is container ready for traffic? | Remove from service | Slow startup, dependencies not ready |

**Liveness Probe Types**:

```yaml
# HTTP probe (most common)
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
    httpHeaders:
    - name: Custom-Header
      value: Awesome
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

# TCP probe (just check port is open)
livenessProbe:
  tcpSocket:
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 20

# Exec probe (run command in container)
livenessProbe:
  exec:
    command:
    - cat
    - /tmp/healthy
  initialDelaySeconds: 5
  periodSeconds: 5
```

**Probe parameters explained**:

- `initialDelaySeconds`: Wait before first check (app startup time)
- `periodSeconds`: How often to check
- `timeoutSeconds`: How long to wait for response
- `failureThreshold`: How many failures before action (restart for liveness)
- `successThreshold`: How many successes needed to be considered healthy (usually 1)

## Real-World Incident Example

**Company**: SaaS platform (500K daily users)  
**Impact**: 45-minute complete outage, 100% of users affected  
**Cost**: $750K in lost revenue + $1.2M in SLA refunds = $1.95M  

**What happened**:
A developer added a liveness probe to a critical authentication service:

```yaml
livenessProbe:
  httpGet:
    path: /v2/health  # New endpoint in v2 branch
    port: 8080
  failureThreshold: 2
  periodSeconds: 5
```

Problem: The PR merged but the `/v2/health` endpoint wasn't in the deployed code yet—it was on a different branch! The health endpoint was actually `/health` (v1).

**The cascade**:

```
14:00 - Deployment starts
14:01 - First pod starts, liveness probe fails (404)
14:01 - Pod restarted (failure threshold: 2, so 10 seconds to kill)
14:01 - Old pod terminated (RollingUpdate)
14:01 - New pod starts, fails again
14:02 - All 50 pods in restart loop
14:03 - Service has 0 healthy endpoints
14:03 - 100% of users see "Service Unavailable"
14:03 - On-call paged, team scrambles
14:20 - Team identifies liveness probe issue
14:25 - Quick fix: kubectl edit deployment, change /v2/health → /health
14:30 - Pods stabilize
14:45 - Service fully recovered
```

**Why it was catastrophic**:
1. **No gradual rollout** - All pods updated at once
2. **No pre-production testing** - Liveness probe never tested in staging
3. **Fast failure** - failureThreshold: 2 with periodSeconds: 5 = 10 second kill time
4. **Authentication service** - When it's down, entire platform is down

**The fix**: 
```bash
kubectl edit deployment auth-service
# Changed path from /v2/health to /health
# Pods recovered immediately
```

**Lessons learned**:
1. Always test health endpoints before deploying
2. Use longer initial delays for slow-starting apps
3. Set higher failure thresholds (3-5) to tolerate transient issues
4. Use progressive rollouts (not all at once)
5. Monitor restart counts - alert if pods restart repeatedly

## Commands You Mastered

```bash
# Check restart counts
kubectl get pods -n <namespace>
# Look at RESTARTS column

# Describe pod to see liveness probe failures
kubectl describe pod <name> -n <namespace>
# Look at Events: "Liveness probe failed"

# Check deployment probe configuration
kubectl get deployment <name> -n <namespace> -o yaml | grep -A 20 livenessProbe

# Edit deployment (fix probe config)
kubectl edit deployment <name> -n <namespace>

# Check probe results in real-time
kubectl get events -n <namespace> --watch

# View container logs (might show probe requests)
kubectl logs <pod> -n <namespace>
```

## Best Practices for Liveness Probes

### ✅ DO:

1. **Use appropriate initialDelaySeconds**:
   ```yaml
   initialDelaySeconds: 30  # Give app time to start
   ```

2. **Set reasonable failure thresholds**:
   ```yaml
   failureThreshold: 3  # Allow some transient failures
   ```

3. **Keep health checks lightweight**:
   ```go
   // Bad: Health check does database query
   // Good: Health check just returns 200 OK
   ```

4. **Use separate liveness and readiness probes**:
   ```yaml
   livenessProbe:
     httpGet:
       path: /healthz  # Is process alive?
   readinessProbe:
     httpGet:
       path: /ready    # Is service ready for traffic?
   ```

5. **Test in staging first**:
   - Deploy to staging with new probe
   - Verify pods stay healthy
   - Then deploy to production

### ❌ DON'T:

1. **Don't use same probe for liveness and readiness**:
   - Liveness = "restart me if broken"
   - Readiness = "don't send traffic yet"

2. **Don't make health checks expensive**:
   ```yaml
   # Bad: Checks database, does cleanup, runs migrations
   # Good: Returns 200 if process is running
   ```

3. **Don't use very short periods**:
   ```yaml
   periodSeconds: 1  # Too aggressive! Creates load
   periodSeconds: 10 # Better
   ```

4. **Don't forget initialDelaySeconds**:
   ```yaml
   # Bad: App needs 20s to start but initialDelay is 5s
   # Result: Immediate restart loop!
   ```

## Debugging Restart Loops

**Step-by-step**:

```bash
# 1. Check if pods are restarting
kubectl get pods -n <namespace>

# 2. If RESTARTS is increasing, describe the pod
kubectl describe pod <name> -n <namespace>

# 3. Look for:
#    - "Liveness probe failed" in Events
#    - "Back-off restarting failed container"

# 4. Check probe configuration
kubectl get deployment <name> -n <namespace> -o yaml | grep -A 20 livenessProbe

# 5. Test the health endpoint manually
kubectl port-forward pod/<name> 8080:8080 -n <namespace>
curl http://localhost:8080/healthz  # Should return 200

# 6. If endpoint is wrong, fix it
kubectl edit deployment <name> -n <namespace>
```

## What's Next?

You've learned how to configure liveness probes correctly. 

Next level: Readiness probes! You'll learn how to prevent traffic from reaching pods before they're ready to handle requests.

**Key takeaway**: Liveness probes should be simple and reliable. When in doubt, use a TCP socket probe or a very basic HTTP endpoint that just returns 200.
