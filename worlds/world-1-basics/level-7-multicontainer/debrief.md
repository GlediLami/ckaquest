# 🎓 Mission Debrief: Sidecar Sabotage

## What Happened

Your pod had two containers: a main app and a log-sidecar. The sidecar tried to `tail -f` a file that didn't exist, causing it to crash immediately. In Kubernetes, **if any container in a pod crashes, the entire pod is considered unhealthy**.

## How Kubernetes Behaved

Multi-container pods run all containers **simultaneously on the same node** and **share certain resources**:

- **Network**: Same IP address, can communicate via localhost
- **Volumes**: Can share storage via volumeMounts
- **Lifecycle**: Pod is Ready only when ALL containers are Ready

Your pod lifecycle:
1. Both containers started
2. main-app: Started successfully ✅
3. log-sidecar: Crashed (file not found) ❌
4. Kubernetes restarted log-sidecar
5. Crashed again → CrashLoopBackOff
6. Pod shows "1/2" ready (one container working, one failing)

## The Correct Mental Model

**Why multi-container pods?**

Common patterns:

| Pattern | Main Container | Sidecar Container | Use Case |
|---------|----------------|-------------------|----------|
| **Sidecar** | Web app | Log forwarder | Ship logs to Elasticsearch |
| **Ambassador** | App | Proxy | Connect to external services |
| **Adapter** | Legacy app | Format converter | Convert logs to standard format |

**Pod as atomic unit**:
```
┌─────────────────── Pod ───────────────────┐
│  ┌──────────┐        ┌──────────┐        │
│  │  main    │◄─────► │  sidecar │        │
│  │  app     │ share  │  logging │        │
│  └──────────┘ volume └──────────┘        │
│       ↓                    ↓              │
│  Same network namespace                   │
│  Same IP: 10.244.0.5                      │
└───────────────────────────────────────────┘
```

**Container states in a pod**:
- All must be Running → Pod is Running
- Any crashes → Pod shows reduced ready count (e.g., 1/2)
- All crash → Pod enters CrashLoopBackOff

## Real-World Incident Example

**Company**: Media streaming platform (50M users)  
**Impact**: 12-hour degraded service, 2M users affected  
**Cost**: $3.5M in refunds + brand damage

**What happened**:
The platform used a sidecar pattern: main container served video, sidecar collected metrics. During a routine update, someone changed the metrics sidecar's configuration file path from `/config/metrics.yaml` to `/etc/metrics.yaml`.

The file wasn't at the new path. Sidecar crashed. Pod showed "1/2" ready. Kubernetes deployment strategy was "RollingUpdate" with `maxUnavailable: 0`, meaning it wouldn't replace old pods until new ones were Ready.

**Result**: Deployment stuck—new pods never became fully Ready (2/2), so old pods kept running. But the deployment was marked as "in progress" so no one could deploy fixes!

**Why it took 12 hours**:
- Team thought deployment was successful (75% of replicas were "running")
- Monitoring only checked pod existence, not readiness
- Finally discovered by checking: `kubectl get pods` showed "1/2" across all new pods
- Checked logs: `kubectl logs <pod> -c metrics-sidecar` showed "file not found"

**The fix**: Corrected the config path. All pods became 2/2 Ready immediately.

**Lesson**: 
1. Monitor container readiness, not just pod existence
2. Test sidecar containers independently
3. Set deployment timeout to fail fast
4. Alert on pods with partial ready states

## Commands You Mastered

```bash
# View all containers in a pod
kubectl get pod <name> -n <namespace> -o jsonpath='{.spec.containers[*].name}'

# Check ready status (shows X/Y containers ready)
kubectl get pod <name> -n <namespace>

# See status of each container
kubectl describe pod <name> -n <namespace>

# View logs from specific container
kubectl logs <pod-name> -c <container-name> -n <namespace>

# View logs with previous container instance (if crashed)
kubectl logs <pod-name> -c <container-name> --previous -n <namespace>

# Follow logs in real-time
kubectl logs <pod-name> -c <container-name> -f -n <namespace>

# Execute command in specific container
kubectl exec <pod-name> -c <container-name> -it -n <namespace> -- sh

# Stream logs from all containers
kubectl logs <pod-name> --all-containers=true -f -n <namespace>
```

## Multi-Container Best Practices

1. **Keep sidecars simple**: They should be lightweight and focused
2. **Handle missing files**: Use scripts that create files if they don't exist
3. **Set proper restart policies**: RestartPolicy: Always (default) keeps retrying
4. **Resource limits**: Sidecars need resources too! Don't starve main container
5. **Health checks**: Implement readiness probes for both containers
6. **Logging**: Ensure both containers log to stdout/stderr for easy debugging

## Debugging Multi-Container Pods

Step-by-step process:

```bash
# 1. Check overall pod status
kubectl get pod <name> -n <namespace>
# Look for X/Y in READY column (e.g., 1/2 means one container failed)

# 2. Identify which container is failing
kubectl describe pod <name> -n <namespace>
# Look at "Container Statuses" section

# 3. Check logs of failing container
kubectl logs <pod> -c <failing-container> -n <namespace>

# 4. Check previous logs if container is crash looping
kubectl logs <pod> -c <failing-container> --previous -n <namespace>

# 5. Test interactively if possible
kubectl exec <pod> -c <container> -it -n <namespace> -- sh
# Then manually run the command to see what fails
```

## Common Multi-Container Pitfalls

| Issue | Symptom | Solution |
|-------|---------|----------|
| Sidecar crashes | "1/2" ready | Check sidecar logs, fix command |
| Port conflict | CrashLoopBackOff | Ensure containers use different ports |
| Resource starvation | One container OOMKilled | Set proper resource requests/limits |
| Volume permissions | Permission denied | Fix volume mount permissions |
| Startup race | Init failed | Use init containers for dependencies |

## What's Next?

You've mastered multi-container debugging! Next challenge: A mysterious application failure that's only visible in the logs—time to become a log detective! 🕵️
