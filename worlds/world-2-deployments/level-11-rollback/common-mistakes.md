# Common Mistakes - Level 11: Deployment Rollback

## ❌ Mistake #1: Rolling Back Without Checking History

**What players try:**
```bash
kubectl rollout undo deployment/payment-api -n rollback
# Hope it fixes everything!
```

**Why it fails:**
By default, `undo` goes back ONE revision. But what if:
- The problem started 3 deployments ago?
- You've already rolled back once (so "undo" goes forward!)?
- The previous version also had issues?

**Correct approach:**
```bash
# FIRST: Check the history
kubectl rollout history deployment/payment-api -n rollback

# See what changed in each revision
kubectl rollout history deployment/payment-api --revision=2 -n rollback
kubectl rollout history deployment/payment-api --revision=3 -n rollback

# THEN: Rollback to known good revision
kubectl rollout undo deployment/payment-api --to-revision=2 -n rollback
```

**Key Learning:**
Always review rollout history before blindly running `undo`. You need to know which revision was good!

---

## ❌ Mistake #2: Not Waiting for Rollout to Complete

**What players try:**
```bash
kubectl rollout undo deployment/payment-api -n rollback
./validate.sh  # Immediate validation!
```

**Why it fails:**
Rollouts are **asynchronous**. The undo command returns immediately, but the actual rollout takes time (creating new pods, terminating old ones).

**Correct approach:**
```bash
# Start the rollback
kubectl rollout undo deployment/payment-api --to-revision=2 -n rollback

# WAIT for it to complete
kubectl rollout status deployment/payment-api -n rollback

# Or watch pods change
kubectl get pods -n rollback -w
# Press Ctrl+C when all pods are Running

# NOW validate
./validate.sh
```

**Key Learning:**
Use `kubectl rollout status` to wait for rollout completion. Don't validate while pods are still updating!

---

## ❌ Mistake #3: Confusing ReplicaSets with Revisions

**What players try:**
```bash
kubectl get rs -n rollback
# See multiple ReplicaSets
# Delete the old ones thinking it will help
kubectl delete rs payment-api-abc123 -n rollback
```

**Why it fails:**
Each deployment revision creates a ReplicaSet. Old ReplicaSets are kept for rollback history. Deleting them:
- Removes your rollback ability
- Doesn't fix the current deployment
- Can cause issues with rollout management

**Correct approach:**
```bash
# View ReplicaSets (but don't delete them)
kubectl get rs -n rollback -l app=payment-api

# See which ReplicaSet is active (has pods)
kubectl describe deployment payment-api -n rollback | grep -A 5 "NewReplicaSet"

# Let Deployment manage ReplicaSets - never delete manually
```

**Key Learning:**
ReplicaSets = Deployment's internal mechanism for version control. Don't touch them directly!

---

## ❌ Mistake #4: Forgetting Why Rollback is Needed

**What players try:**
Focus only on executing the rollback command, forget to understand WHY the deployment failed.

**Why it fails:**
You might roll back successfully but not learn:
- What went wrong in the new version?
- How to prevent this in the future?
- What to check before deploying?

**Correct approach:**
```bash
# BEFORE rollback: Understand the failure
kubectl describe deployment payment-api -n rollback
kubectl get pods -n rollback
kubectl logs deployment/payment-api -n rollback

# THEN rollback
kubectl rollout undo deployment/payment-api --to-revision=2 -n rollback

# AFTER rollback: Verify the difference
kubectl rollout history deployment/payment-api --revision=2 -n rollback
kubectl rollout history deployment/payment-api --revision=3 -n rollback
```

**Key Learning:**
Rollback is a recovery mechanism, not a learning shortcut. Understand the failure to prevent repeats!

---

## ❌ Mistake #5: Not Checking Rollout History Limit

**What players try:**
Expect to roll back 10 revisions ago.

**Why it fails:**
Deployments have `revisionHistoryLimit` (default: 10). After 10 deployments, old ReplicaSets are garbage collected.

**Correct approach:**
```yaml
# In deployment spec
spec:
  revisionHistoryLimit: 10  # Adjust if needed
  # ...
```

```bash
# Check how many revisions are kept
kubectl get deployment payment-api -n rollback -o jsonpath='{.spec.revisionHistoryLimit}'

# See available history
kubectl rollout history deployment/payment-api -n rollback
```

**Key Learning:**
You can only roll back as far as `revisionHistoryLimit` allows. Default is 10 revisions.

---

## ❌ Mistake #6: Using `kubectl edit` for Rollback

**What players try:**
```bash
kubectl edit deployment payment-api -n rollback
# Manually change image tag back to old version
```

**Why it fails:**
This creates a NEW revision, not a rollback. You:
- Lose the clean rollback history
- Create confusion about which revision is which
- May introduce typos

**Correct approach:**
```bash
# Use the proper rollback command
kubectl rollout undo deployment/payment-api --to-revision=2 -n rollback

# NOT kubectl edit!
```

**Key Learning:**
`kubectl edit` = new deployment. `kubectl rollout undo` = proper rollback with history intact.

---

## ❌ Mistake #7: Checking Wrong Resource

**What players try:**
```bash
# Check pods directly
kubectl get pods -n rollback

# Don't check deployment status
```

**Why it fails:**
Pods come and go during rollouts. The Deployment is the source of truth for:
- Desired state
- Rollout progress
- Available replicas

**Correct approach:**
```bash
# Check Deployment first
kubectl get deployment payment-api -n rollback

# Output shows:
# NAME          READY   UP-TO-DATE   AVAILABLE
# payment-api   3/3     3            3

# READY = current/desired
# UP-TO-DATE = pods with latest template
# AVAILABLE = pods passing readiness checks
```

**Key Learning:**
Deployments manage pods. Check the Deployment status, not just individual pods.

---

## ❌ Mistake #8: Not Understanding Rollout Status Output

**What players try:**
```bash
kubectl rollout status deployment/payment-api -n rollback
# See "Waiting for deployment spec update to be observed..."
# Think it's broken
```

**Why it fails:**
This message is normal! It means Kubernetes is processing your rollback. Other normal messages:
- "Waiting for deployment spec update..."
- "Waiting for rollout to finish: X out of Y new replicas..."
- "deployment successfully rolled out" ← Success!

**Correct approach:**
```bash
kubectl rollout status deployment/payment-api -n rollback
# WAIT for: "deployment successfully rolled out"
# If it hangs, Ctrl+C and check:
kubectl describe deployment payment-api -n rollback
kubectl get events -n rollback --sort-by='.lastTimestamp'
```

**Key Learning:**
`kubectl rollout status` shows real-time progress. Wait for "successfully rolled out" message.

---

## 💡 Debugging Workflow - The Right Way

Here's the systematic rollback approach:

```bash
# 1. Identify the problem
kubectl get deployment payment-api -n rollback
kubectl get pods -n rollback
kubectl logs deployment/payment-api -n rollback

# 2. Check rollout history
kubectl rollout history deployment/payment-api -n rollback

# 3. Identify last known good revision
kubectl rollout history deployment/payment-api --revision=2 -n rollback

# 4. Initiate rollback to specific revision
kubectl rollout undo deployment/payment-api --to-revision=2 -n rollback

# 5. Wait for completion
kubectl rollout status deployment/payment-api -n rollback

# 6. Verify success
kubectl get deployment payment-api -n rollback
kubectl get pods -n rollback

# 7. Test functionality (if applicable)
kubectl logs deployment/payment-api -n rollback

# 8. Validate
./validate.sh
```

---

## 🎯 Key Takeaways

1. **Check history before rollback** - Know which revision to target
2. **Use `--to-revision=N`** - Don't rely on default "undo"
3. **Wait for rollout completion** - Use `kubectl rollout status`
4. **Don't delete ReplicaSets manually** - Deployment manages them
5. **Understand the failure** - Learn what went wrong before rolling back
6. **Check Deployment status** - Not just individual pods
7. **Use proper rollback commands** - Not `kubectl edit`
8. **Revision history is limited** - Default 10, can't roll back forever

---

## 📊 Rollout History Explained

```bash
$ kubectl rollout history deployment/payment-api -n rollback
REVISION  CHANGE-CAUSE
1         Initial deployment
2         Updated to v1.2.0
3         Updated to v1.3.0 (BROKEN)

# Current = Revision 3
# kubectl rollout undo → Goes to Revision 2
# kubectl rollout undo --to-revision=1 → Goes to Revision 1
```

**Each revision is stored as a ReplicaSet:**
- Revision 1 → payment-api-abc123 (0 pods)
- Revision 2 → payment-api-def456 (0 pods)
- Revision 3 → payment-api-ghi789 (3 pods) ← Current

**After rollback to revision 2:**
- Revision 2 → payment-api-def456 (3 pods) ← Now current
- Revision 3 → payment-api-ghi789 (0 pods)
- Revision 4 created (same as revision 2)

---

## 📚 What You Should Know After This Level

✅ How to view deployment rollout history  
✅ How to rollback to specific revision  
✅ How to wait for rollout completion  
✅ Understanding of ReplicaSet relationship to revisions  
✅ How to verify successful rollback  
✅ Difference between `undo` and `edit`  
✅ How to read deployment status output  

**Next Level Preview:** Level 12 covers liveness probes - when deployments succeed but pods keep restarting!
