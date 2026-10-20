# Common Mistakes - Level 1: CrashLoopBackOff

## ❌ Mistake #1: Not Checking Previous Logs

**What players try:**
```bash
kubectl logs nginx-broken -n k8squest
```

**Why it fails:**
The container is crashing so fast that by the time you run this command, the new container has no logs yet (or minimal logs). You need the logs from the PREVIOUS crashed container.

**Correct approach:**
```bash
kubectl logs nginx-broken --previous -n k8squest
```

**Key Learning:**
The `--previous` flag shows logs from the last terminated container, which is exactly what you need when debugging crashes.

---

## ❌ Mistake #2: Trying to Edit a Running Pod

**What players try:**
```bash
kubectl edit pod nginx-broken -n k8squest
# Try to change the command field
```

**Why it fails:**
Most pod spec fields (including `command`) are **immutable** after creation. Kubernetes will reject your changes or they won't take effect.

**Correct approach:**
```bash
# Delete the broken pod
kubectl delete pod nginx-broken -n k8squest

# Apply the fixed YAML
kubectl apply -f solution.yaml -n k8squest
```

**Key Learning:**
When the pod spec needs to change, you must recreate the pod. This is why Deployments exist - they handle this for you!

---

## ❌ Mistake #3: Fixing the Wrong Container

**What players try:**
In multi-container pods, players often fix the first container in the YAML without checking which one is actually crashing.

**Why it fails:**
Events and status will show "Container 'app' is crashing" but you fixed container 'nginx'. Always check which specific container is failing.

**Correct approach:**
```bash
# Check which container is failing
kubectl describe pod nginx-broken -n k8squest | grep -A 5 "State:"

# Or look at container status
kubectl get pod nginx-broken -n k8squest -o jsonpath='{.status.containerStatuses[*].name}'
```

**Key Learning:**
Always identify the exact container that's failing before making changes.

---

## ❌ Mistake #4: Not Understanding Exit Codes

**What players try:**
See "Exit Code: 127" in describe output but don't understand what it means.

**Why it fails:**
Exit codes tell you WHY the container crashed:
- **Exit 0**: Normal exit (success)
- **Exit 1**: General error
- **Exit 127**: Command not found
- **Exit 137**: Killed by OOM (Out of Memory)
- **Exit 143**: Terminated (SIGTERM)

**Correct approach:**
```bash
kubectl describe pod nginx-broken -n k8squest | grep "Exit Code"
```

If you see **Exit Code: 127**, the command doesn't exist or isn't in PATH.

**Key Learning:**
- **127 → Command not found** (typo in command or missing binary)
- **137 → OOMKilled** (memory limit too low)
- **1 → Application error** (check logs for details)

---

## ❌ Mistake #5: Applying broken.yaml Again

**What players try:**
```bash
kubectl apply -f broken.yaml -n k8squest
# Hope it works this time?
```

**Why it fails:**
Applying the same broken config won't fix the issue! You need to modify the YAML or create a fixed version.

**Correct approach:**
1. Copy broken.yaml to a new file
2. Edit the new file with fixes
3. Apply the fixed file

```bash
cp broken.yaml my-fix.yaml
# Edit my-fix.yaml
kubectl apply -f my-fix.yaml -n k8squest
```

**Key Learning:**
`kubectl apply` doesn't "retry" - it enforces whatever config you give it. Fix the config first!

---

## ❌ Mistake #6: Ignoring Events

**What players try:**
Focus only on pod status and logs, skip events.

**Why it fails:**
Events contain crucial debugging info like:
- Why scheduling failed
- When probes failed
- Image pull errors
- Resource quota violations

**Correct approach:**
```bash
# Always check events as part of debugging
kubectl get events -n k8squest --sort-by='.lastTimestamp'

# Or check events for specific pod
kubectl describe pod nginx-broken -n k8squest | grep -A 20 Events
```

**Key Learning:**
Events are Kubernetes' way of telling you what went wrong. They're sorted by time and show the sequence of failures.

---

## ❌ Mistake #7: Not Testing the Fix

**What players try:**
Change the YAML and immediately run validate.

**Why it fails:**
You need to actually apply the changes and verify the pod is running before validation.

**Correct approach:**
```bash
# 1. Delete old pod
kubectl delete pod nginx-broken -n k8squest

# 2. Apply fix
kubectl apply -f solution.yaml -n k8squest

# 3. Verify it's running
kubectl get pod nginx-broken -n k8squest

# 4. Wait for Running status
kubectl wait --for=condition=ready pod/nginx-broken -n k8squest --timeout=60s

# 5. NOW validate
./validate.sh
```

**Key Learning:**
Always verify your fix manually before running validation. kubectl get/describe/logs are your friends!

---

## ❌ Mistake #8: Forgetting Namespace

**What players try:**
```bash
kubectl get pods
# No pods found!
```

**Why it fails:**
By default, kubectl looks in the `default` namespace. K8sQuest uses the `k8squest` namespace.

**Correct approach:**
```bash
# Always specify namespace
kubectl get pods -n k8squest

# Or set default namespace for session
kubectl config set-context --current --namespace=k8squest
```

**Key Learning:**
Namespaces isolate resources. Always use `-n k8squest` or set it as default.

---

## 💡 Debugging Workflow - The Right Way

Here's the systematic approach that works:

```bash
# 1. Check current status
kubectl get pods -n k8squest

# 2. Get detailed info
kubectl describe pod nginx-broken -n k8squest

# 3. Check PREVIOUS logs (for crashes)
kubectl logs nginx-broken --previous -n k8squest

# 4. Check events
kubectl get events -n k8squest --sort-by='.lastTimestamp' | tail -20

# 5. Identify the issue from above info

# 6. Fix the YAML

# 7. Delete and recreate
kubectl delete pod nginx-broken -n k8squest
kubectl apply -f solution.yaml -n k8squest

# 8. Verify fix
kubectl get pod nginx-broken -n k8squest -w
# Wait for Running status (Ctrl+C to stop)

# 9. Validate
./validate.sh
```

---

## 🎯 Key Takeaways

1. **Always check previous logs** when debugging crashes (`--previous` flag)
2. **Pod specs are mostly immutable** - delete and recreate to change them
3. **Events are your friend** - they show the timeline of what went wrong
4. **Exit codes matter** - 127 = command not found, 137 = OOMKilled
5. **Specify namespace** - use `-n k8squest` or set default context
6. **Test before validate** - verify with kubectl before running validation
7. **Fix the config, not just the symptom** - understand WHY it crashed

---

## 📚 What You Should Know After This Level

✅ How to read previous container logs  
✅ How to interpret CrashLoopBackOff status  
✅ How to identify which container is failing  
✅ How to fix command errors in pod specs  
✅ How to delete and recreate pods  
✅ How to use events for debugging  
✅ Understanding of exit codes  

**Next Level Preview:** Level 2 teaches ImagePullBackOff debugging - different symptoms, similar systematic approach!
