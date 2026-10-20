# 🎯 World 1: Basics - Quick Reference Card

> **Print this page and keep it by your keyboard!**

## 🔧 Essential kubectl Commands

### Investigation & Debugging
```bash
# Check pod status
kubectl get pods -n ckaquest

# Detailed pod information
kubectl describe pod <pod-name> -n ckaquest

# View container logs
kubectl logs <pod-name> -n ckaquest

# View logs for specific container in multi-container pod
kubectl logs <pod-name> -c <container-name> -n ckaquest

# Stream logs in real-time
kubectl logs -f <pod-name> -n ckaquest

# Get previous container logs (after crash)
kubectl logs <pod-name> --previous -n ckaquest

# Check events (critical for debugging!)
kubectl get events -n ckaquest --sort-by='.lastTimestamp'

# Interactive shell into running container
kubectl exec -it <pod-name> -n ckaquest -- /bin/sh
```

### Resource Management
```bash
# List all resources in namespace
kubectl get all -n ckaquest

# Delete and recreate pod
kubectl delete pod <pod-name> -n ckaquest
kubectl apply -f <file.yaml> -n ckaquest

# Force delete stuck pod
kubectl delete pod <pod-name> -n ckaquest --grace-period=0 --force

# Check resource quotas
kubectl get resourcequota -n ckaquest
kubectl describe resourcequota -n ckaquest
```

### YAML Editing
```bash
# Apply changes from file
kubectl apply -f broken.yaml -n ckaquest

# Edit live resource (dangerous!)
kubectl edit pod <pod-name> -n ckaquest

# View current YAML
kubectl get pod <pod-name> -n ckaquest -o yaml

# Dry-run to test changes
kubectl apply -f solution.yaml -n ckaquest --dry-run=client
```

---

## 🚨 Debugging Flowchart

```
Pod not running?
    │
    ├─→ Status: Pending
    │   ├─→ Check: kubectl describe pod
    │   ├─→ Look for: Insufficient resources, PVC issues, node selector
    │   └─→ Fix: Adjust requests/limits, check storage, fix scheduling
    │
    ├─→ Status: CrashLoopBackOff
    │   ├─→ Check: kubectl logs <pod> --previous
    │   ├─→ Look for: Application errors, missing config, wrong command
    │   └─→ Fix: Correct command, add config, fix app code
    │
    ├─→ Status: ImagePullBackOff
    │   ├─→ Check: kubectl describe pod (look at Events)
    │   ├─→ Look for: Wrong image name, missing tag, private registry
    │   └─→ Fix: Correct image name, add imagePullSecrets
    │
    ├─→ Status: Running but not working
    │   ├─→ Check: kubectl logs <pod>
    │   ├─→ Check: kubectl get svc (service endpoints)
    │   ├─→ Look for: Port mismatch, label selector wrong, app errors
    │   └─→ Fix: Match ports, fix labels, debug application
    │
    └─→ Status: Error/Unknown
        ├─→ Check: kubectl get events
        ├─→ Check: kubectl describe pod
        └─→ Look for: Node issues, API server problems, RBAC
```

---

## 💡 Common Patterns & Solutions

### Pattern 1: Crash Loop
**Symptoms:** Pod restarts repeatedly, Back-off restarting failed container  
**First Check:** `kubectl logs <pod> --previous`  
**Common Causes:**
- Wrong command or arguments
- Missing environment variables
- Application code bugs
- Missing dependencies

**Quick Fix Template:**
```yaml
containers:
- name: app
  command: ["/bin/sh"]  # ✅ Override wrong command
  args: ["-c", "sleep 3600"]  # ✅ Test command
```

### Pattern 2: Image Pull Failure
**Symptoms:** ImagePullBackOff, ErrImagePull  
**First Check:** `kubectl describe pod <pod>` (Events section)  
**Common Causes:**
- Typo in image name
- Missing tag (defaults to :latest which may not exist)
- Private registry without credentials

**Quick Fix Template:**
```yaml
containers:
- name: app
  image: nginx:1.21  # ✅ Add explicit tag
  # ❌ image: ngnix:latest (typo)
```

### Pattern 3: Pending Forever
**Symptoms:** Pod stays in Pending, never schedules  
**First Check:** `kubectl describe pod <pod>` (look for "FailedScheduling")  
**Common Causes:**
- Insufficient CPU/memory
- PersistentVolumeClaim not bound
- Node selector doesn't match any nodes
- ResourceQuota exceeded

**Quick Fix Template:**
```yaml
resources:
  requests:
    memory: "64Mi"   # ✅ Reduce if too high
    cpu: "100m"      # ✅ 100m = 0.1 CPU core
  limits:
    memory: "128Mi"
    cpu: "200m"
```

### Pattern 4: Label Selector Mismatch
**Symptoms:** Service has no endpoints, pods not selected  
**First Check:** 
```bash
kubectl get pods --show-labels -n ckaquest
kubectl describe svc <service> -n ckaquest
```

**Common Causes:**
- Typo in label key or value
- Case sensitivity (app vs App)
- Missing labels on pods

**Quick Fix Template:**
```yaml
# Service selector MUST match Pod labels
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app  # ✅ Must match pod labels exactly
---
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: my-app  # ✅ Matches service selector
```

---

## 🎓 Pro Tips

### Tip 1: Events Are Your Friend
**Always check events when stuck:**
```bash
kubectl get events -n ckaquest --sort-by='.lastTimestamp' | tail -20
```
Events show you what Kubernetes tried to do and why it failed.

### Tip 2: Previous Logs After Crash
**Container crashed? Get the logs from before it died:**
```bash
kubectl logs <pod> --previous -n ckaquest
```
Without `--previous`, you only see logs from current (crashed) container.

### Tip 3: Describe Everything
**`kubectl describe` is more detailed than `kubectl get`:**
```bash
kubectl describe pod <pod> -n ckaquest
# Shows: Events, status, conditions, volumes, QoS, more
```

### Tip 4: Use Short Names
```bash
kubectl get po    # pods
kubectl get svc   # services
kubectl get deploy # deployments
kubectl get rs    # replicasets
kubectl get ns    # namespaces
```

### Tip 5: Watch Mode
**See changes in real-time:**
```bash
kubectl get pods -n ckaquest -w
# Press Ctrl+C to stop watching
```

---

## 📊 Status Code Reference

| Status | Meaning | First Thing to Check |
|--------|---------|---------------------|
| `Pending` | Pod accepted but not scheduled | `kubectl describe pod` → Events |
| `Running` | Pod scheduled and at least 1 container running | `kubectl logs` |
| `Succeeded` | All containers terminated successfully | Nothing (this is good!) |
| `Failed` | All containers terminated, at least 1 failed | `kubectl logs --previous` |
| `Unknown` | Pod state unknown (node issue) | `kubectl get nodes` |
| `CrashLoopBackOff` | Container keeps crashing | `kubectl logs --previous` |
| `ImagePullBackOff` | Can't pull container image | `kubectl describe pod` → Events |
| `CreateContainerError` | Can't create container | `kubectl describe pod` |
| `InvalidImageName` | Image name malformed | Check image: field in YAML |

---

## 🔍 Container State Reference

| State | Meaning | Common Cause |
|-------|---------|--------------|
| `Waiting: ContainerCreating` | Normal startup | Wait or check events if stuck |
| `Waiting: CrashLoopBackOff` | Crashed multiple times | Check logs `--previous` |
| `Waiting: ImagePullBackOff` | Image pull failed | Wrong image name/tag |
| `Waiting: ErrImagePull` | First image pull attempt failed | Check image availability |
| `Running` | Container is running | ✅ Good! |
| `Terminated: Completed` | Exited successfully (code 0) | ✅ Good for jobs! |
| `Terminated: Error` | Exited with error | Check exit code and logs |

---

## 🎯 Learning Objectives - World 1

By completing World 1, you should be able to:

- ✅ **Debug CrashLoopBackOff** - Read logs, understand exit codes
- ✅ **Fix ImagePullBackOff** - Correct image names and tags
- ✅ **Resolve Pending Pods** - Adjust resource requests, fix scheduling
- ✅ **Fix Label Selectors** - Match service selectors to pod labels
- ✅ **Debug Port Mismatches** - Align containerPort with service targetPort
- ✅ **Work with Multi-Container Pods** - Specify container names in commands
- ✅ **Find Logs in Multi-Container** - Use `-c <container>` flag
- ✅ **Debug Init Containers** - Understand init container lifecycle
- ✅ **Work with Namespaces** - Manage resources in specific namespaces
- ✅ **Handle Resource Quotas** - Stay within namespace limits

---

## 📚 Additional Resources

### Official Kubernetes Docs
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

### CKAQuest Resources
- Use `guide` command in game for step-by-step walkthroughs
- Use `hints` command for progressive hints (3 levels)
- Read `debrief.md` after completing each level for deep learning

---

## 🚀 Quick Wins Checklist

When stuck on a level, try these in order:

- [ ] `kubectl get pods -n ckaquest` - What's the status?
- [ ] `kubectl describe pod <pod> -n ckaquest` - Check Events section
- [ ] `kubectl logs <pod> -n ckaquest` - Any application errors?
- [ ] `kubectl logs <pod> --previous -n ckaquest` - If crashed, check previous logs
- [ ] `kubectl get events -n ckaquest --sort-by='.lastTimestamp'` - Recent events
- [ ] Compare `broken.yaml` with expected behavior - What's different?
- [ ] Use `hints` in game - Get nudge in right direction
- [ ] Use `guide` in game - Step-by-step solution if really stuck

**Remember:** The goal is learning, not speed. Take time to understand WHY each fix works!

---

💡 **Pro Tip:** Keep this reference open in a browser tab while playing. Use Ctrl+F to quickly find commands!

🎮 **Ready to play?** Run `./play.sh` and start learning!
