# 🎓 Mission Debrief: Init Container Gridlock

## What Happened

Your init container was waiting for a service that doesn't exist. Init containers must complete before main containers start, so your pod was stuck in "Init:0/1" status forever.

## How Kubernetes Behaved

**Init containers** run before app containers and must complete successfully:

1. Init containers run sequentially (one after another)
2. Each must exit with status 0 (success)
3. Only after ALL init containers complete do app containers start
4. If init container fails, pod restarts (subject to restartPolicy)

## The Correct Mental Model

**Lifecycle**:
```
Init Container 1 → Init Container 2 → Main Container 1 & Main Container 2
  (sequential)       (sequential)          (parallel)
```

**Common use cases**:
- Wait for dependencies (databases, services)
- Clone git repositories
- Generate configuration files
- Set up permissions
- Database schema migrations

## Commands You Mastered

```bash
# Check init container status
kubectl get pod <name> -n <namespace>
# Look for "Init:0/1" or "Init:Error"

# View init container logs
kubectl logs <pod> -c <init-container-name> -n <namespace>

# See init container details
kubectl describe pod <name> -n <namespace>
# Look at "Init Containers:" section
```

## What's Next

Final level: Namespace isolation issues!
