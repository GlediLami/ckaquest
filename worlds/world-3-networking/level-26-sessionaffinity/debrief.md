# Level 26: Session Affinity Missing - Mission Debrief

## Mission Overview

**Objective:** Fix a stateful application that was losing user sessions by configuring session affinity on the Kubernetes Service.

**XP Awarded:** 200 XP  
**Difficulty:** Intermediate  
**Concepts:** Session Affinity (Sticky Sessions), Service Load Balancing, Stateful vs Stateless Applications

---

## What You Encountered

You deployed a web application that stores user sessions in memory—a common pattern in legacy applications. Users could log in successfully, but their subsequent requests showed them as logged out. The application worked intermittently, with users randomly logged in or out.

The culprit? The Service was load-balancing requests randomly across multiple pods, and session data only existed in the pod that handled the login.

**The Broken Configuration:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: session-service
spec:
  selector:
    app: session-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  # ❌ MISSING: sessionAffinity: ClientIP
```

**The Problem:**
- Service uses default load-balancing (random/round-robin)
- Request 1: User logs in → Pod 1 (session stored in Pod 1's memory)
- Request 2: User loads page → Pod 2 (no session! User appears logged out)
- Request 3: User tries again → Pod 3 (no session! Still logged out)
- Request 4: User tries again → Pod 1 (session found! Logged in again)
- Result: Inconsistent, frustrating user experience

---

## The Root Cause: Missing Session Affinity

### Understanding Kubernetes Service Load Balancing

By default, Kubernetes Services distribute traffic across backend pods using **random** or **round-robin** load balancing. This is ideal for stateless applications where any pod can handle any request.

**Default Behavior (sessionAffinity: None):**

```
┌──────────┐
│  Client  │
│  Request │
└────┬─────┘
     │
     ▼
┌─────────────────────┐
│  Service            │
│  Random selection   │
└─────────────────────┘
     │
     ├───────────┬───────────┐
     ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Pod 1  │ │  Pod 2  │ │  Pod 3  │
│ Session │ │   No    │ │   No    │
│  Data   │ │ Session │ │ Session │
└─────────┘ └─────────┘ └─────────┘
```

Each request can go to ANY pod. If session data is stored in memory, only the pod that handled the login has it.

### What is Session Affinity?

Session affinity (also called "sticky sessions") ensures requests from the same client IP consistently route to the same backend pod.

**With Session Affinity (sessionAffinity: ClientIP):**

```
┌──────────────────┐
│  Client          │
│  IP: 10.244.0.5  │
└────┬─────────────┘
     │
     ▼
┌──────────────────────────┐
│  Service                 │
│  hash(10.244.0.5) = 2    │
│  Always pick Pod 2       │
└──────────────────────────┘
     │
     ├───────────┬───────────┐
     │           │           │
     ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Pod 1  │ │  Pod 2  │ │  Pod 3  │
│         │ │ ✅ Gets │ │         │
│         │ │  ALL    │ │         │
│         │ │ Requests│ │         │
└─────────┘ └─────────┘ └─────────┘
```

All requests from the same client IP go to the same pod, preserving session state.

---

## The Fix Explained

**What You Added:**

```yaml
# BEFORE (broken)
spec:
  selector:
    app: session-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080

# AFTER (solution)
spec:
  selector:
    app: session-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  sessionAffinity: ClientIP          # Enable sticky sessions
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800          # 3 hours (default)
```

**How It Works:**

1. **First Request:**
   - Client IP: 10.244.0.5
   - Service calculates: `hash(10.244.0.5) % 3 = 2`
   - Routes to Pod 2
   - Stores mapping: `10.244.0.5 → Pod 2`

2. **Subsequent Requests:**
   - Client IP: 10.244.0.5 (same)
   - Service checks mapping: `10.244.0.5 → Pod 2`
   - Routes to Pod 2 (consistent!)

3. **Timeout:**
   - Mapping expires after `timeoutSeconds` (default: 10800s / 3 hours)
   - Next request creates new mapping (may go to different pod)

**Implementation:**

Kubernetes uses **kube-proxy** to implement session affinity via iptables (or IPVS) rules:

```bash
# Example iptables rule (simplified)
iptables -t nat -A KUBE-SVC-XXX -m statistic --mode random --probability 0.33 -j KUBE-SEP-POD1
iptables -t nat -A KUBE-SVC-XXX -m statistic --mode random --probability 0.50 -j KUBE-SEP-POD2
iptables -t nat -A KUBE-SVC-XXX -j KUBE-SEP-POD3

# With sessionAffinity: ClientIP, iptables uses -m recent to track source IPs
iptables -t nat -A KUBE-SVC-XXX -m recent --rcheck --seconds 10800 --name POD1 -j KUBE-SEP-POD1
```

---

## Real-World Incident: The Shopping Cart Disaster

**Company:** E-commerce retailer (electronics & gadgets)  
**Date:** Black Friday, November 2020  
**Impact:** 12 hours of chaos, 8,000+ support tickets, $4.7M in lost sales  

### What Happened

The company was migrating from a monolithic application to microservices. The legacy shopping cart service stored cart data in memory (not ideal, but it worked with a single server).

During Black Friday preparation, the team scaled the cart service from 1 pod to 10 pods to handle expected traffic. They tested checkout, and it worked fine. They didn't test the full user journey.

**The Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cart-service
spec:
  replicas: 10        # Scaled up from 1
  selector:
    matchLabels:
      app: cart
---
apiVersion: v1
kind: Service
metadata:
  name: cart-service
spec:
  selector:
    app: cart
  ports:
  - port: 8080
  # ❌ No sessionAffinity configured!
```

### The Problem

**User Journey:**
1. User adds item to cart → Request goes to Pod 3 (cart stored in Pod 3's memory)
2. User continues shopping → Request goes to Pod 7 (cart appears empty!)
3. User adds another item → Request goes to Pod 2 (cart only has this new item)
4. User goes to checkout → Request goes to Pod 3 (cart has first item from step 1!)
5. User sees wrong items, gets confused, abandons cart

**Black Friday Timeline:**

**6:00 AM:** Black Friday sale starts  
**6:15 AM:** First complaints: "My cart is empty!"  
**6:30 AM:** Support tickets flooding in (200+ in 15 minutes)  
**7:00 AM:** Engineering team alerted (1,000+ tickets now)  
**7:30 AM:** Team identifies pattern: carts randomly emptying  
**8:00 AM:** Database team checks for data loss (nothing wrong)  
**9:00 AM:** Someone suggests: "Are we load-balancing across pods?"  
**9:30 AM:** Root cause identified: Session affinity missing  
**10:00 AM:** Hotfix deployed: Added sessionAffinity: ClientIP  
**10:30 AM:** Validation: Cart behavior normalized  
**6:00 PM:** Full recovery, support backlog cleared  

### The Damage

- **8,000+ support tickets** (average Black Friday: 500)
- **35% cart abandonment rate** (vs. 20% normally)
- **$4.7M in lost sales** (estimated from abandonment spike)
- **Brand damage** (social media complaints, negative reviews)
- **Engineering overtime** (entire team worked 18-hour shifts)

### The Hotfix

```yaml
apiVersion: v1
kind: Service
metadata:
  name: cart-service
spec:
  selector:
    app: cart
  ports:
  - port: 8080
  sessionAffinity: ClientIP      # ✅ ADDED
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600       # 1 hour (shorter for shopping sessions)
```

**Why 1 hour timeout?**
- Shopping sessions typically last 30-45 minutes
- Longer timeout (3+ hours) caused uneven load distribution
- 1 hour balanced session persistence with load balancing

### The Long-Term Fix

The team didn't stop at session affinity—they refactored the cart service:

**Phase 1: Immediate (Same Day)**
- Added sessionAffinity: ClientIP
- Set timeout to 1 hour
- Monitored cart behavior

**Phase 2: Week 1**
- Migrated cart data to Redis (shared storage)
- All pods read/write to same Redis instance
- Session affinity still enabled for safety

**Phase 3: Week 2**
- Removed session affinity (no longer needed)
- Fully stateless cart service
- Any pod can handle any request

**Final Architecture:**
```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  Pod 1  │────▶│  Redis  │◀────│  Pod 2  │
└─────────┘     │  (Cart  │     └─────────┘
                │  Data)  │
┌─────────┐     │         │     ┌─────────┐
│  Pod 3  │────▶│         │◀────│  Pod 4  │
└─────────┘     └─────────┘     └─────────┘

All pods share cart data → No session affinity needed!
```

### Lessons Learned

1. **Test Full User Journeys:**
   - Don't just test individual API endpoints
   - Test complete workflows (browse → add to cart → checkout)
   - Use realistic traffic patterns in staging

2. **Understand Stateful Dependencies:**
   - Identify which services store state in memory
   - Document dependencies before scaling
   - Have migration plan for stateful components

3. **Monitor Session Behavior:**
   - Track cart abandonment rates
   - Alert on unexpected spikes
   - Monitor "empty cart" errors

4. **Plan for Failure:**
   - Session affinity is a band-aid, not a cure
   - Plan migration to stateless architecture
   - Use session affinity as temporary bridge

5. **Load Test Scaled Deployments:**
   - Test with multiple replicas BEFORE Black Friday
   - Simulate real user behavior (multi-step transactions)
   - Verify sessions persist across requests

---

## Session Affinity Deep Dive

### Configuration Options

**Basic Configuration:**
```yaml
spec:
  sessionAffinity: ClientIP
```

**With Timeout:**
```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800    # Default: 3 hours
```

### Timeout Values

**timeoutSeconds Range:** 1 to 86400 (1 second to 24 hours)

**Common Values:**
- **3600** (1 hour): Shopping carts, active browsing sessions
- **7200** (2 hours): File uploads, long-running operations
- **10800** (3 hours): Default, general web applications
- **28800** (8 hours): Business applications, workday sessions
- **86400** (24 hours): Maximum, rarely needed

**Choosing Timeout:**

Consider:
1. **Average session duration** (analytics data)
2. **Load distribution** (shorter = better distribution)
3. **Business requirements** (user expectations)
4. **Pod churn rate** (sessions lost on pod restart anyway)

```yaml
# E-commerce site (30-minute average session)
timeoutSeconds: 3600   # 1 hour (some buffer)

# Video streaming (2-3 hour movies)
timeoutSeconds: 14400  # 4 hours

# Financial portal (all-day usage)
timeoutSeconds: 28800  # 8 hours
```

### Supported Values

```yaml
sessionAffinity: None       # Default, no affinity
sessionAffinity: ClientIP   # Route by client IP
```

**NOTE:** Kubernetes only supports these two values. No other options (like cookie-based affinity) at the Service level. For advanced routing, use an Ingress controller.

---

## Stateful vs Stateless Applications

### Stateful Application (Session Affinity Needed)

```
┌───────────────────────────────────┐
│  Pod 1                            │
│  ┌─────────────────────────────┐  │
│  │ In-Memory Session Storage   │  │
│  │ user123: {cart: [item1]}    │  │
│  │ user456: {cart: [item2]}    │  │
│  └─────────────────────────────┘  │
└───────────────────────────────────┘
```

**Characteristics:**
- Session data stored in pod's memory
- Sessions lost if pod restarts
- Requires sticky sessions (session affinity)
- Uneven load distribution
- Scaling challenges

**Examples:**
- Legacy web applications with server-side sessions
- File upload services (streaming to same pod)
- WebSocket connections (require same pod)
- In-memory caching without distributed cache

### Stateless Application (No Session Affinity)

```
┌─────────┐     ┌──────────────────┐
│  Pod 1  │────▶│  Redis/Database  │
└─────────┘     │  user123: {...}  │
                │  user456: {...}  │
┌─────────┐     └──────────────────┘
│  Pod 2  │────▶         ▲
└─────────┘              │
                         │
┌─────────┐              │
│  Pod 3  │──────────────┘
└─────────┘
```

**Characteristics:**
- Session data in shared storage (Redis, database)
- Any pod can handle any request
- Even load distribution
- Easy horizontal scaling
- Sessions survive pod restarts

**Examples:**
- Modern web applications with Redis sessions
- REST APIs with JWT authentication (token-based)
- Microservices with external state management
- Cloud-native applications

### Comparison Table

| Aspect                  | Stateful (with affinity) | Stateless                |
|-------------------------|--------------------------|--------------------------|
| **Load Distribution**   | Uneven (sticky sessions) | Even (any pod)           |
| **Scaling**             | Limited (session loss)   | Easy (no state)          |
| **Pod Restart**         | Sessions lost ❌          | Sessions persist ✅       |
| **Complexity**          | Low (simple setup)       | Medium (shared storage)  |
| **Cloud-Native**        | No ❌                     | Yes ✅                    |
| **Recommended**         | Legacy/temporary only    | Modern applications      |

---

## How to Make Your App Stateless

### Option 1: Shared Session Storage (Redis)

**Before (stateful):**
```python
# In-memory session (stored in pod's RAM)
from flask import Flask, session
app = Flask(__name__)
app.secret_key = 'secret'

@app.route('/login')
def login():
    session['user_id'] = 123    # Stored in THIS pod's memory
    return "Logged in"

@app.route('/profile')
def profile():
    user_id = session.get('user_id')  # Only works on SAME pod!
    return f"User {user_id}"
```

**After (stateless with Redis):**
```python
from flask import Flask
from flask_session import Session
import redis

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://redis-service:6379')
Session(app)

@app.route('/login')
def login():
    session['user_id'] = 123    # Stored in Redis (shared)
    return "Logged in"

@app.route('/profile')
def profile():
    user_id = session.get('user_id')  # Works from ANY pod!
    return f"User {user_id}"
```

**Deployment:**
```yaml
# Redis deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7
        ports:
        - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
  - port: 6379
```

### Option 2: JWT Tokens (Fully Stateless)

**Before (session-based):**
```python
@app.route('/login')
def login():
    session['user_id'] = 123
    session['email'] = 'user@example.com'
    return "Logged in"
```

**After (JWT tokens):**
```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'your-secret-key'

@app.route('/login')
def login():
    # Create JWT token with user data
    payload = {
        'user_id': 123,
        'email': 'user@example.com',
        'exp': datetime.utcnow() + timedelta(hours=3)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return {'token': token}

@app.route('/profile')
def profile():
    # Verify and decode token (no server-side session!)
    token = request.headers.get('Authorization').split()[1]
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    return f"User {user_id}"
```

**Benefits:**
- No server-side session storage
- No shared Redis needed
- Scales infinitely (stateless)
- Works across multiple services (microservices)

### Option 3: Database-backed Sessions

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://db-service/sessions'
db = SQLAlchemy(app)

class Session(db.Model):
    session_id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer)
    data = db.Column(db.JSON)
    expires_at = db.Column(db.DateTime)
```

All pods read/write to the same database.

---

## Tradeoffs and When to Use Session Affinity

### When to USE Session Affinity ✅

1. **Legacy Applications:**
   - Can't easily refactor to stateless
   - Migration in progress (use affinity as bridge)
   - Third-party applications you can't modify

2. **WebSocket Connections:**
   - Long-lived connections require same pod
   - Chat applications, real-time dashboards
   - Game servers

3. **File Uploads:**
   - Large file streaming to same pod
   - Progress tracking in memory
   - Temporary until upload completes

4. **Quick Fixes:**
   - Production incident (immediate mitigation)
   - Buying time to implement proper solution
   - Short-term compatibility during migration

### When to AVOID Session Affinity ❌

1. **New Applications:**
   - Design stateless from the start
   - Use JWT, shared sessions, or external state
   - Follow cloud-native principles

2. **High Availability:**
   - Sessions lost on pod restart/failure
   - Poor user experience during deployments
   - No graceful degradation

3. **Auto-scaling:**
   - New pods get no traffic initially (uneven load)
   - Scale-down kills active sessions
   - Metrics misleading (some pods idle, others busy)

4. **Multi-region:**
   - Session affinity doesn't cross regions
   - User switches regions → new session
   - Shared storage (Redis) works globally

### Limitations

**1. Pod Failures:**
```
User Session → Pod 2 (dies) → Session lost!
Next request → Pod 1 (no session) → User logged out
```

**2. Deployments:**
```
Rolling update:
Pod 1 (old) → Terminated → Active sessions lost
Pod 2 (new) → Users need to re-login
```

**3. Load Distribution:**
```
Pod 1: 100 sessions (heavy load)
Pod 2: 10 sessions (idle)
Pod 3: 5 sessions (mostly idle)

Uneven resource utilization!
```

**4. IP-based Limitations:**
```
User behind NAT/proxy:
1000 users → Same source IP → All go to Pod 1
Result: Pod 1 overloaded, others idle
```

---

## Debugging Session Affinity

### 1. Verify Configuration

```bash
# Check if sessionAffinity is configured
kubectl get service session-service -n k8squest -o yaml | grep -A3 sessionAffinity
```

Expected output:
```yaml
sessionAffinity: ClientIP
sessionAffinityConfig:
  clientIP:
    timeoutSeconds: 10800
```

### 2. Test Sticky Behavior

```bash
# Make multiple requests from same pod (same IP)
kubectl exec client -n k8squest -- sh -c 'for i in 1 2 3 4 5; do wget -q -O- http://session-service; echo; done'
```

All responses should be from the **same pod**.

### 3. Test Different IPs Get Different Pods

```bash
# Create second client pod
kubectl run client2 -n k8squest --image=busybox:1.36 -- sleep 3600

# Request from client2 (different source IP)
kubectl exec client2 -n k8squest -- wget -q -O- http://session-service
```

client2 **may** get a different pod than client (good for load distribution).

### 4. Check kube-proxy Mode

```bash
# Check if kube-proxy is running
kubectl get pods -n kube-system -l k8s-app=kube-proxy

# Check kube-proxy mode (iptables or IPVS)
kubectl logs -n kube-system kube-proxy-xxxxx | grep "Using"
```

Session affinity works with both iptables and IPVS modes.

### 5. Monitor Session Distribution

```bash
# Watch logs to see session distribution
kubectl logs -f client -n k8squest
```

After timeout expires, requests MAY go to different pod.

### 6. Force New Session Mapping

```bash
# Delete and recreate client pod (new IP = new mapping)
kubectl delete pod client -n k8squest
kubectl run client -n k8squest --image=busybox:1.36 --command -- sh -c 'while true; do wget -q -O- http://session-service 2>&1; sleep 2; done'
```

New client IP will get new pod assignment.

---

## Best Practices

### 1. Use Session Affinity as Temporary Solution

```
Phase 1: Deploy with sessionAffinity (quick fix)
Phase 2: Implement shared session storage (proper fix)
Phase 3: Remove sessionAffinity (no longer needed)
```

### 2. Set Appropriate Timeout

```yaml
# Shopping cart (30-min average session)
timeoutSeconds: 3600   # 1 hour

# Video streaming (2-hour movies)
timeoutSeconds: 10800  # 3 hours

# Business app (8-hour workday)
timeoutSeconds: 28800  # 8 hours
```

Don't use 24-hour timeout unless absolutely necessary (poor load distribution).

### 3. Monitor Uneven Load

```bash
# Check CPU/memory per pod
kubectl top pods -n k8squest -l app=session-app
```

If one pod uses 90% CPU and others use 10%, session affinity may be causing uneven load.

### 4. Document Migration Plan

```yaml
# Add annotation to Service
metadata:
  annotations:
    migration-plan: "Using sessionAffinity as temporary fix. Migrating to Redis by Q2 2024."
    ticket: "JIRA-12345"
```

### 5. Graceful Shutdown

```yaml
# Give pods time to finish active requests
spec:
  terminationGracePeriodSeconds: 60  # Wait 60s before force-kill
  containers:
  - name: app
    lifecycle:
      preStop:
        exec:
          command: ["/bin/sh", "-c", "sleep 30"]  # Wait 30s for connections to drain
```

### 6. Health Checks

```yaml
# Don't mark pod ready until sessions initialized
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
readinessProbe:
  httpGet:
    path: /ready    # Check if session store is accessible
    port: 8080
```

---

## Key Takeaways

1. **Session Affinity Ensures Consistency:**
   - `sessionAffinity: ClientIP` routes requests from same IP to same pod
   - Critical for stateful applications with in-memory sessions
   - Simple configuration, but has significant tradeoffs

2. **Timeout Matters:**
   - `timeoutSeconds` controls how long affinity lasts
   - Balance session persistence vs load distribution
   - Shorter = better load balance, longer = fewer session losses

3. **Stateless is Better:**
   - Session affinity is a band-aid for stateful apps
   - Modern apps should use shared session storage (Redis)
   - Or token-based authentication (JWT) for full statelessness
   - Cloud-native = stateless by default

4. **Tradeoffs:**
   - ✅ Simple setup, works with legacy apps
   - ❌ Uneven load, sessions lost on pod restart, poor scalability

5. **Real-World Lessons:**
   - Session affinity issues can cause massive customer impact ($4.7M!)
   - Always test full user journeys with multiple replicas
   - Monitor session behavior and cart abandonment
   - Have migration plan to stateless architecture

---

## What's Next?

You've mastered session affinity and understand stateful vs stateless design! You now know:
- ✅ How to configure sessionAffinity: ClientIP
- ✅ When to use (and when NOT to use) session affinity
- ✅ Tradeoffs between stateful and stateless architectures
- ✅ How to migrate from stateful to stateless

In the next levels, you'll explore cross-namespace service communication, service endpoint updates, and more advanced networking patterns.

**Continue your K8sQuest journey to unlock the next challenge!** 🚀

---

## Additional Resources

- [Kubernetes Service Documentation](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Session Affinity](https://kubernetes.io/docs/reference/networking/virtual-ips/#session-affinity)
- [Stateful vs Stateless Applications](https://12factor.net/)
- [Redis for Session Storage](https://redis.io/docs/manual/programmability/sessions/)

---

**Mission Complete!** 🎉  
You've earned 200 XP and understood the tradeoffs of sticky sessions!
