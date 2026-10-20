# 🎓 Mission Debrief: ImagePullBackOff Mystery

## What Happened

Your pod was stuck in `ImagePullBackOff` status because Kubernetes couldn't pull the container image `nginx:nonexistent-tag-xyz-123` from Docker Hub. This tag doesn't exist, so the kubelet kept trying and backing off between attempts.

## How Kubernetes Behaved

When you create a pod, Kubernetes goes through several phases:

1. **Pending**: Pod accepted, waiting to be scheduled
2. **ContainerCreating**: Scheduled, pulling images
3. **Running**: All containers started successfully

Your pod got stuck at phase 2. The kubelet on the node tried to pull the image, failed, waited a bit (backoff), and tried again. This creates the `ImagePullBackOff` status.

## The Correct Mental Model

**Container images** are like blueprints for your application. They consist of:
- **Repository**: Where the image lives (e.g., `nginx`, `mysql`, `myapp`)
- **Tag**: A specific version (e.g., `latest`, `1.21`, `v2.0.3`)
- **Full reference**: `repository:tag` (e.g., `nginx:1.21`)

**Image pull process**:
```
kubectl apply → Scheduler assigns node → Kubelet pulls image → Creates container → Pod runs
                                             ↑
                                        You were stuck here!
```

Common mistakes:
- Typos in image names
- Non-existent tags
- Private images without pull secrets
- Wrong registry URLs

## Real-World Incident Example

**Company**: Major e-commerce platform  
**Impact**: 2-hour outage during product launch  
**Cost**: $800K in lost sales

**What happened**: 
A developer pushed code with image tag `v2.3.1` but the CI/CD pipeline built `v2.3.0`. The deployment referenced the non-existent `v2.3.1` tag. All pods went into ImagePullBackOff during a critical product launch.

**Why it lasted 2 hours**:
- No monitoring alerts for ImagePullBackOff
- Team assumed deployment succeeded (it did—pods just couldn't start)
- Spent time debugging application code instead of checking image availability

**The fix**: They noticed the issue in `kubectl describe pod`, fixed the tag, and pods started in 30 seconds.

**Lesson**: Always verify your image exists before deploying. Use `docker pull <image>` locally or check your container registry UI.

## Commands You Mastered

```bash
# Check pod status
kubectl get pod <name> -n <namespace>

# See detailed events (this is your best friend!)
kubectl describe pod <name> -n <namespace>

# Check the exact image being used
kubectl get pod <name> -n <namespace> -o yaml | grep image:

# Delete and recreate a pod
kubectl delete pod <name> -n <namespace>
kubectl apply -f <file>.yaml
```

## Prevention Strategies

1. **Use specific tags**, not `latest` in production
2. **Implement image scanning** in CI/CD to verify images exist
3. **Set up alerts** for ImagePullBackOff events
4. **Use admission controllers** to validate image references before deployment
5. **Keep a local registry mirror** for critical images

## What's Next?

You've now mastered two pod failure modes:
- ✅ CrashLoopBackOff (bad container command)
- ✅ ImagePullBackOff (bad image reference)

Next, you'll learn about pod scheduling issues when resources aren't available!
