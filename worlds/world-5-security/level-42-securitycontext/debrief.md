# 🎓 LEVEL 42 DEBRIEF: Container SecurityContext & Privilege Escalation

**Congratulations!** You've secured containers using Kubernetes SecurityContext - a critical skill for production deployments!

---

## 📊 What You Fixed

**The Problem:**
```yaml
securityContext:
  runAsNonRoot: true  # Enforced but...
  # ❌ No runAsUser specified!
  # ❌ No allowPrivilegeEscalation setting!
```

**Result:** Pod rejected with "container has runAsNonRoot and image will run as root"

**The Solution:**
```yaml
securityContext:
  runAsNonRoot: true  # ✅ Validate
  runAsUser: 1000  # ✅ Specify non-root UID
  allowPrivilegeEscalation: false  # ✅ Prevent escalation
  capabilities:
    drop:
    - ALL  # ✅ Minimal permissions
```

**Result:** Container runs securely as non-root user with minimal privileges

---

## 🔐 Understanding SecurityContext

### What is SecurityContext?

SecurityContext defines **privilege and access control settings** for pods and containers.

**Think of it as:**
- **WHO** the container runs as (user ID)
- **WHAT** privileges it has (capabilities)
- **HOW** it can interact with the host (privilege escalation)

### Two Levels of SecurityContext

#### 1. Pod-Level SecurityContext

```yaml
apiVersion: v1
kind: Pod
spec:
  securityContext:  # ← Pod level (affects all containers)
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
  containers:
  - name: app
```

**Applies to:**
- All containers in the pod
- Volume permissions (fsGroup)
- Shared process namespace

#### 2. Container-Level SecurityContext

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    securityContext:  # ← Container level (overrides pod level)
      runAsUser: 2000
      allowPrivilegeEscalation: false
```

**Applies to:**
- Just this container
- Overrides pod-level settings
- More granular control

---

## 🎯 SecurityContext Fields Reference

### User and Group Settings

#### runAsUser

```yaml
securityContext:
  runAsUser: 1000  # Run as UID 1000
```

**Purpose:** Specifies which user ID the container runs as

**Values:**
- `0` = root (avoid in production!)
- `1000+` = non-root users (recommended)
- `65534` = nobody (minimal permissions)

**Use cases:**
- Override image's default user
- Enforce non-root execution
- Match file ownership requirements

#### runAsGroup

```yaml
securityContext:
  runAsGroup: 3000  # Primary group GID 3000
```

**Purpose:** Sets the primary group ID

**Use with:** File access, shared volumes

#### runAsNonRoot

```yaml
securityContext:
  runAsNonRoot: true  # Enforce non-root
```

**Purpose:** Validates container doesn't run as UID 0

**Behavior:**
- `true`: Kubernetes rejects if user is root
- `false` or unset: Allows root

**Important:** This is a **validation check**, not a setting. You must also set `runAsUser` to a non-zero value.

#### fsGroup (Pod-level only)

```yaml
spec:
  securityContext:
    fsGroup: 2000
```

**Purpose:** Sets ownership of mounted volumes

**Effect:**
- Volume files owned by group `fsGroup`
- Container's primary group set to `fsGroup`

**Use case:** Multiple containers accessing same volume

### Privilege Settings

#### allowPrivilegeEscalation

```yaml
securityContext:
  allowPrivilegeEscalation: false
```

**Purpose:** Controls if process can gain more privileges

**What it blocks:**
- Setuid binaries
- File capabilities
- Other privilege escalation methods

**Best practice:** Always set to `false`

#### privileged

```yaml
securityContext:
  privileged: true  # ⚠️ Dangerous!
```

**Purpose:** Gives container almost all host capabilities

**When to use:** Almost never! Only for:
- System-level daemons
- Device access (GPU, hardware)

**Risk:** Container can escape to host

#### capabilities

```yaml
securityContext:
  capabilities:
    drop:
    - ALL  # Remove all capabilities
    add:
    - NET_BIND_SERVICE  # Add only what's needed
```

**Purpose:** Fine-grained Linux capabilities control

**Common capabilities:**
- `NET_BIND_SERVICE`: Bind to ports < 1024
- `SYS_TIME`: Modify system time
- `NET_ADMIN`: Network configuration

**Best practice:**
1. Drop ALL capabilities
2. Add back only what's required

### Other Security Settings

#### readOnlyRootFilesystem

```yaml
securityContext:
  readOnlyRootFilesystem: true
```

**Purpose:** Makes root filesystem read-only

**Effect:**
- Container can't write to `/`
- Prevents malware persistence
- Increases security

**Use case:** Stateless applications

#### seLinuxOptions

```yaml
securityContext:
  seLinuxOptions:
    level: "s0:c123,c456"
```

**Purpose:** SELinux context (Linux security module)

**Use:** Advanced security policies

---

## 💥 Common SecurityContext Mistakes

### Mistake 1: runAsNonRoot Without runAsUser

```yaml
# ❌ Wrong
securityContext:
  runAsNonRoot: true  # Enforces non-root...
  # But image defaults to root!
# Result: Pod rejected
```

**Fix:**
```yaml
# ✅ Correct
securityContext:
  runAsNonRoot: true
  runAsUser: 1000  # Specify which user
```

### Mistake 2: Forgetting allowPrivilegeEscalation

```yaml
# ❌ Incomplete security
securityContext:
  runAsUser: 1000
  # Missing: allowPrivilegeEscalation: false
# Container can still escalate to root!
```

**Fix:**
```yaml
# ✅ Complete security
securityContext:
  runAsUser: 1000
  allowPrivilegeEscalation: false
```

### Mistake 3: Using Privileged Mode

```yaml
# ❌ Extremely dangerous
securityContext:
  privileged: true  # Full host access!
```

**Fix:** Don't use privileged mode unless absolutely necessary. Use capabilities instead:
```yaml
# ✅ Specific permissions
securityContext:
  capabilities:
    add:
    - NET_ADMIN  # Only network admin
```

### Mistake 4: Running as Root

```yaml
# ❌ Security risk
securityContext:
  runAsUser: 0  # Root user
```

**Fix:**
```yaml
# ✅ Non-root
securityContext:
  runAsUser: 1000
  runAsNonRoot: true
```

### Mistake 5: Port < 1024 as Non-Root

```yaml
# ❌ Won't work
spec:
  securityContext:
    runAsUser: 1000
  containers:
  - ports:
    - containerPort: 80  # Privileged port!
```

**Fix:**
```yaml
# ✅ Use non-privileged port
spec:
  securityContext:
    runAsUser: 1000
  containers:
  - ports:
    - containerPort: 8080  # Non-privileged
```

Or add capability:
```yaml
securityContext:
  runAsUser: 1000
  capabilities:
    add:
    - NET_BIND_SERVICE  # Allow binding to port 80
```

---

## 🚨 REAL-WORLD HORROR STORY: The Cryptomining Container Escape

### The Incident: $400K in Compute Costs + Data Breach

**Company:** Software-as-a-Service platform  
**Date:** September 2023  
**Impact:** Container escape, cryptomining, customer data access, $400K AWS bill

### What Happened

Development team deployed a web application:

```yaml
# Production deployment - NO SecurityContext!
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: web-app
        image: company/web-app:latest
        # ❌ No securityContext!
        # Container runs as root by default
```

**The Vulnerabilities:**
1. Container running as **root** (UID 0)
2. **privileged: true** (left from debugging!)
3. No **allowPrivilegeEscalation: false**
4. Full capabilities (none dropped)

**The Attack Chain:**

1. **Day 1, 10:00** - Vulnerable dependency in web app exploited
2. **10:05** - Attacker gains shell in container
3. **10:10** - Container running as root → full container control
4. **10:15** - privileged: true → attacker escapes to host node
5. **10:20** - Node's kubelet credentials accessed
6. **10:30** - Cluster-wide access obtained
7. **11:00** - Cryptomining software deployed to ALL nodes
8. **12:00** - Customer database pods accessed
9. **Day 3** - Finance team notices $130K AWS bill (2 days)
10. **Day 4** - Security team detects anomalous CPU usage
11. **Day 5** - Breach confirmed, emergency response

### The Damage

**Financial:**
- $400K in compute costs (cryptomining)
- $1.2M in incident response
- $800K in customer compensation
- $3M in lost revenue (service downtime)
- **Total: $5.4M**

**Security:**
- Customer database accessed
- 50,000 customer records potentially exposed
- Regulatory fines pending

**Reputation:**
- Customer trust damaged
- Major customer churned
- Public disclosure required

### Root Causes

1. **No SecurityContext** - Containers ran as root
2. **privileged: true** - Left from debugging, never removed
3. **No security review** - Manifests not reviewed
4. **No Pod Security Standards** - No enforcement
5. **No runtime monitoring** - Cryptomining not detected early

### What Could Have Prevented It

```yaml
# ✅ Secure configuration
spec:
  template:
    spec:
      containers:
      - name: web-app
        image: company/web-app:latest
        securityContext:
          runAsNonRoot: true  # ✅ Prevents root
          runAsUser: 1000  # ✅ Specific non-root user
          allowPrivilegeEscalation: false  # ✅ Blocks escalation
          readOnlyRootFilesystem: true  # ✅ Prevents persistence
          capabilities:
            drop:
            - ALL  # ✅ Minimal permissions
```

**With this SecurityContext:**
1. Container wouldn't run as root → harder to exploit
2. privileged: false (default) → can't escape to host
3. allowPrivilegeEscalation: false → can't gain root
4. No capabilities → limited damage
5. Attack stopped at container boundary

**Additional Safeguards:**
- Pod Security Standards enforced
- Runtime security monitoring
- Network policies limiting egress
- Regular security scanning

### Lessons Learned

1. **Always use SecurityContext** - Never run as root
2. **Review manifests** - Security review required
3. **Enforce Pod Security Standards** - Cluster-level policies
4. **Remove debugging settings** - privileged: true is dangerous
5. **Monitor runtime behavior** - Detect anomalies
6. **Defense in depth** - Multiple security layers

---

## 🛡️ SecurityContext Best Practices

### 1. Always Run as Non-Root

```yaml
# ✅ Secure default for all containers
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
```

### 2. Disable Privilege Escalation

```yaml
securityContext:
  allowPrivilegeEscalation: false
```

### 3. Drop All Capabilities

```yaml
securityContext:
  capabilities:
    drop:
    - ALL
    add: []  # Add only if absolutely needed
```

### 4. Use Read-Only Root Filesystem

```yaml
securityContext:
  readOnlyRootFilesystem: true
volumes:
- name: tmp
  emptyDir: {}  # For /tmp writes
```

### 5. Set fsGroup for Shared Volumes

```yaml
spec:
  securityContext:
    fsGroup: 2000
  containers:
  - volumeMounts:
    - name: data
      mountPath: /data
```

### 6. Never Use privileged: true

```yaml
# ❌ NEVER in production
securityContext:
  privileged: true

# ✅ Use specific capabilities instead
securityContext:
  capabilities:
    add:
    - NET_ADMIN  # Only what's needed
```

### 7. Complete Secure Template

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  securityContext:  # Pod-level
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:latest
    securityContext:  # Container-level
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}
```

---

## 🎯 Pod Security Standards

Kubernetes defines three security profiles:

### 1. Privileged (Least Restrictive)

- No restrictions
- For trusted, system-level workloads

### 2. Baseline (Minimal Restrictions)

```yaml
# Must have:
- No privileged containers
- No hostPath volumes
- No host networking
```

### 3. Restricted (Most Secure)

```yaml
# Must have all of Baseline plus:
securityContext:
  runAsNonRoot: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
  seccompProfile:
    type: RuntimeDefault
```

**Best practice:** Use **Restricted** for all application workloads.

---

## 🔍 Debugging SecurityContext Issues

### Check Pod Events

```bash
kubectl describe pod <pod-name>
```

Look for:
- "container has runAsNonRoot and image will run as root"
- "containers must run as non-root"

### Verify Current Settings

```bash
# Pod-level
kubectl get pod <pod-name> -o jsonpath='{.spec.securityContext}' | jq

# Container-level
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[0].securityContext}' | jq
```

### Check Actual Runtime User

```bash
kubectl exec <pod-name> -- id
# Should show: uid=1000 (not uid=0)
```

### Verify Capabilities

```bash
kubectl exec <pod-name> -- grep Cap /proc/1/status
```

---

## 📚 Quick Reference

| Setting | Purpose | Recommended Value |
|---------|---------|-------------------|
| `runAsUser` | User ID to run as | `1000` (non-root) |
| `runAsNonRoot` | Validate non-root | `true` |
| `allowPrivilegeEscalation` | Block privilege gain | `false` |
| `readOnlyRootFilesystem` | Read-only root | `true` |
| `capabilities.drop` | Remove capabilities | `["ALL"]` |
| `fsGroup` | Volume group ownership | `2000` |
| `privileged` | Full host access | `false` (never use) |

---

## 🎯 Key Takeaways

1. **Always use SecurityContext** - Never deploy without it
2. **Run as non-root** - runAsUser + runAsNonRoot
3. **Disable privilege escalation** - allowPrivilegeEscalation: false
4. **Drop all capabilities** - Minimal permissions
5. **Use Pod Security Standards** - Enforce cluster-wide
6. **Read-only filesystem** - Prevents malware persistence
7. **Never use privileged mode** - Extreme security risk
8. **Defense in depth** - SecurityContext is one layer of many

---

## 🚀 Next Steps

Now that you understand SecurityContext, you're ready for:

- **Level 43:** ResourceQuota - controlling resource consumption
- **Level 44:** NetworkPolicy - controlling network traffic
- **Level 45:** Node Affinity - advanced scheduling

---

**Excellent work!** You've mastered container security - a critical foundation for production Kubernetes! 🎉🔐
