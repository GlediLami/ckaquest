# 🎓 Mission Debrief: Fix the Crashing Pod

## What Happened

Your pod was crashing because it tried to run a command called `nginxzz` - but that command doesn't exist in the nginx container image.

When you inspected the pod with `kubectl describe`, you saw:
```
Error: failed to create containerd task: exec: "nginxzz": executable file not found in $PATH
```

This is Kubernetes telling you: "I found the image, pulled it, created a container... but the command you told me to run doesn't exist."

## How Kubernetes Behaved

Here's what happened under the hood:

1. **Scheduler** assigned the pod to a node ✅
2. **Kubelet** pulled the nginx image ✅
3. **Container runtime** tried to start the container with command `["nginxzz"]` ❌
4. **Container crashed** immediately
5. **Kubelet** tried again (CrashLoopBackOff)
6. **Exponential backoff** kicked in - wait longer between retries

This is **Kubernetes doing exactly what you told it to do**. It's not smart enough to know `nginxzz` is a typo.

## The Correct Mental Model

### Key Concepts:

1. **Pods are ephemeral**
   - You can't edit most fields of a running pod
   - When you need changes, delete and recreate
   - This is why Deployments exist (they manage this for you)

2. **Container images define what CAN run**
   - The nginx image has: nginx, bash, sh, etc.
   - It doesn't have: nginxzz
   - The `command` field overrides the image's default command

3. **CrashLoopBackOff is feedback**
   - Not a scary error - it's information
   - Tells you: "I keep trying but this keeps failing"
   - The Events in `kubectl describe` tell you WHY

### What You Should Remember:

- **Always check `kubectl describe pod <name>`** - Events tell the story
- **Pods can't be edited after creation** - delete and recreate
- **CrashLoopBackOff = container keeps crashing** - not a network/scheduling issue
- **The command field is dangerous** - only use it when you need to override the default

## Real-World Incident Example

### Scenario: Production Outage at 3 AM

**What happened:**
A developer deployed a new version of an API service. They added a `command` field to run a startup script:

```yaml
command: ["/app/startup.sh"]
```

But they forgot to make the script executable (`chmod +x`). 

**Impact:**
- All pods crashed immediately
- CrashLoopBackOff across the deployment
- API down for 12 minutes
- $50K revenue loss

**Root cause:**
The `command` field tried to execute a file without execute permissions.

**How it was fixed:**
```bash
# Quick fix: Remove the command override
kubectl edit deployment api-service
# (removed the command field - used image's default)

# Proper fix: Made script executable in Dockerfile
RUN chmod +x /app/startup.sh
```

**Lesson:**
- Always test container commands locally first: `docker run --rm -it <image> <command>`
- Use the image's default command when possible
- If you override it, know exactly what you're doing

## How This Applies to Your Career

### Interview Questions You Can Now Answer:

**Q: "A pod is in CrashLoopBackOff. How do you debug it?"**

**A:** 
1. Check pod events: `kubectl describe pod <name>`
2. Check logs: `kubectl logs <name>` (or `--previous` for last crash)
3. Look for: command not found, missing dependencies, config errors
4. Fix the issue and recreate the pod or update the deployment

**Q: "Can you edit a running pod?"**

**A:** 
Only specific fields like:
- `spec.containers[*].image`
- `spec.activeDeadlineSeconds`
- `spec.tolerations` (additions only)

Most changes require deleting and recreating. This is why we use Deployments in production.

## Commands You Mastered

```bash
# Check pod status
kubectl get pod <name> -n <namespace>

# See detailed events and state
kubectl describe pod <name> -n <namespace>

# View logs (even from crashed containers)
kubectl logs <name> -n <namespace>
kubectl logs <name> -n <namespace> --previous

# Delete and recreate
kubectl delete pod <name> -n <namespace>
kubectl apply -f <file>.yaml

# Edit on-the-fly (limited fields)
kubectl edit pod <name> -n <namespace>
```

## Next Steps

You now understand:
- ✅ How to debug crashing pods
- ✅ Why CrashLoopBackOff happens
- ✅ Pod immutability and its implications
- ✅ The power (and danger) of the `command` field

**Next challenge:** We'll look at Deployments - the proper way to manage pods in production.

---

💡 **Pro tip:** In production, you'd almost never use standalone pods. Deployments handle restarts, rollbacks, and scaling. But understanding pods is essential because Deployments create pods under the hood.
