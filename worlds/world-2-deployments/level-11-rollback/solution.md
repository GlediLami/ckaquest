# Solution

```bash
k rollout history deploy web-app -n rollback
k rollout undo deploy web-app -n rollback
k rollout status deploy web-app -n rollback
```

The new pods fail with ImagePullBackOff. `rollout undo` goes back to the previous ReplicaSet, which still has working pods.
