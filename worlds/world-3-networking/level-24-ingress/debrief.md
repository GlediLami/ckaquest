# Level 24: Ingress Path Mismatch - Mission Debrief

## Mission Overview

**Objective:** Fix an Ingress configuration where the path routing was incorrectly configured, causing 404 errors for all requests to the application.

**XP Awarded:** 250 XP  
**Difficulty:** Intermediate  
**Concepts:** Kubernetes Ingress, Path-based Routing, HTTP Routing, PathType

---

## What You Encountered

You deployed a simple web application (nginx) accessible at `http://myapp.local`. Everything seemed configured correctly—the Pod was running, the Service had endpoints, and the Ingress resource existed. Yet when you tried to access the application, you got **404 Not Found** errors.

The culprit? A subtle but critical misconfiguration in the Ingress path.

**The Broken Configuration:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
spec:
  rules:
  - host: myapp.local
    http:
      paths:
      - path: /api        # ❌ WRONG!
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

**The Problem:**
- The application serves content at the **root path** (`/`)
- The Ingress was configured to route traffic for **`/api`**
- When users accessed `http://myapp.local/`, the request didn't match any Ingress rule
- Result: 404 Not Found

---

## The Root Cause: Path Mismatch

### Understanding Ingress Path Matching

Kubernetes Ingress uses **path-based routing** to direct HTTP/HTTPS traffic to different backend services. The `path` field in the Ingress spec determines which requests get routed to which service.

**How Path Matching Works:**

1. **Client makes request:** `http://myapp.local/index.html`
2. **Ingress controller extracts path:** `/index.html`
3. **Ingress controller checks rules:**
   - Does `/index.html` match the configured path?
   - Matching logic depends on `pathType`
4. **Routes to backend or returns 404**

### PathType Options

Kubernetes supports three `pathType` values:

#### 1. **Prefix** (Most Common)
Matches based on path prefix. The path must START with the configured value.

```yaml
path: /api
pathType: Prefix
```

**Matches:**
- `/api` ✅
- `/api/` ✅
- `/api/users` ✅
- `/api/v1/posts` ✅

**Does NOT Match:**
- `/` ❌
- `/app` ❌
- `/application/api` ❌

#### 2. **Exact**
Matches only the exact path, character-for-character.

```yaml
path: /api
pathType: Exact
```

**Matches:**
- `/api` ✅

**Does NOT Match:**
- `/api/` ❌ (trailing slash!)
- `/api/users` ❌
- `/API` ❌ (case-sensitive)

#### 3. **ImplementationSpecific**
Depends on the Ingress controller implementation. Avoid this unless you have specific needs and understand your Ingress controller's behavior.

### Common Path Patterns

```yaml
# Match root and everything
path: /
pathType: Prefix
# Matches: /, /index.html, /css/app.css, /api/users, etc.

# Match only API endpoints
path: /api
pathType: Prefix
# Matches: /api, /api/users, /api/v1/posts
# Does NOT match: /, /app, /home

# Match exact login page
path: /login
pathType: Exact
# Matches: /login only
# Does NOT match: /login/, /login?redirect=home

# Match specific version of API
path: /api/v2
pathType: Prefix
# Matches: /api/v2, /api/v2/users, /api/v2/posts
# Does NOT match: /api/v1, /api/v3
```

---

## The Fix Explained

**What You Changed:**

```yaml
# BEFORE (broken.yaml)
paths:
- path: /api        # Wrong path
  pathType: Prefix
  
# AFTER (solution.yaml)
paths:
- path: /           # Correct path
  pathType: Prefix
```

**Why This Works:**

1. **Requests to `http://myapp.local/`:**
   - Extracted path: `/`
   - Ingress rule: `path: /`, `pathType: Prefix`
   - Match: `/` starts with `/` ✅
   - Routes to: `web-service:80`

2. **Requests to `http://myapp.local/index.html`:**
   - Extracted path: `/index.html`
   - Ingress rule: `path: /`, `pathType: Prefix`
   - Match: `/index.html` starts with `/` ✅
   - Routes to: `web-service:80`

3. **With the broken config (`path: /api`):**
   - Request: `http://myapp.local/`
   - Extracted path: `/`
   - Ingress rule: `path: /api`, `pathType: Prefix`
   - Match: `/` does NOT start with `/api` ❌
   - Result: 404 Not Found (no matching rule)

---

## Real-World Incident: The API Gateway Nightmare

**Company:** E-commerce platform with 2M monthly users  
**Date:** March 2022  
**Impact:** 6 hours of downtime, $180,000 in lost revenue  

### What Happened

The platform was migrating from a monolithic application to microservices. The infrastructure team configured an Ingress to route traffic:

```yaml
# INTENDED ROUTING:
# / → frontend-service (main website)
# /api → backend-service (API)
```

**The Broken Configuration:**
```yaml
spec:
  rules:
  - host: shop.example.com
    http:
      paths:
      - path: /api/v1           # ❌ TOO SPECIFIC!
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8080
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

### The Problem

The API had two versions:
- `/api/v1/*` (old, being deprecated)
- `/api/v2/*` (new, actively used)

**What Went Wrong:**

1. **Day 1:** Deployed new Ingress configuration
   - `/api/v1/products` → Routed to `backend-service` ✅
   - `/api/v2/products` → Routed to `frontend-service` ❌

2. **Frontend service received API requests:**
   - Frontend (React app) doesn't handle API paths
   - Returned: 404 Not Found for all v2 API requests

3. **Mobile app broke completely:**
   - Mobile app ONLY used `/api/v2/*` endpoints
   - All API calls failed: authentication, product listings, checkout
   - 500,000 active users couldn't browse or purchase

4. **Monitoring didn't catch it:**
   - Health checks only tested `/api/v1/health`
   - Those succeeded, so alerts didn't fire
   - Load balancer thought everything was fine

### Timeline

**10:00 AM:** Deployed new Ingress configuration during scheduled maintenance  
**10:15 AM:** Mobile users started reporting "can't load products"  
**10:30 AM:** Customer support flooded with tickets (500+ in 15 minutes)  
**10:45 AM:** Engineering team identified 95% of API calls failing  
**11:00 AM:** Root cause identified: Ingress path mismatch  
**11:15 AM:** Hotfix deployed: Changed `path: /api/v1` to `path: /api`  
**11:30 AM:** Validation complete, traffic restored  
**4:00 PM:** Full post-mortem completed

### The Hotfix

```yaml
# FIXED:
paths:
- path: /api              # ✅ Matches ALL API versions
  pathType: Prefix
  backend:
    service:
      name: backend-service
      port:
        number: 8080
- path: /
  pathType: Prefix
  backend:
    service:
      name: frontend-service
      port:
        number: 80
```

Now:
- `/api/v1/products` → `backend-service` ✅
- `/api/v2/products` → `backend-service` ✅
- `/` → `frontend-service` ✅

### Lessons Learned

1. **Test All Paths:**
   - Don't just test one version of the API
   - Test deprecated AND current endpoints
   - Automate path coverage testing

2. **Order Matters:**
   - Ingress rules are evaluated in order
   - Most specific paths should come FIRST
   - More general paths should come LAST

3. **Monitor Path Coverage:**
   - Track which paths are getting 404s
   - Alert on unexpected 404 spikes
   - Differentiate between "resource not found" and "route not found"

4. **Use Integration Tests:**
   - Test the full request path: DNS → Ingress → Service → Pod
   - Don't rely solely on unit tests or health checks
   - Test from outside the cluster (like real users)

5. **Gradual Rollouts:**
   - Deploy Ingress changes to staging first
   - Use canary deployments for critical routing changes
   - Have instant rollback procedures ready

---

## Advanced Ingress Concepts

### 1. **Path Rewriting**

Sometimes you want the Ingress path to differ from the backend path.

**Example:** Old API at `/api/v1`, new API at `/v2`, but you want users to access both at `/api`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /api(/|$)(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: api-service
            port:
              number: 8080
```

**How It Works:**
- Request: `http://api.example.com/api/users`
- Regex captures: `$2 = "users"`
- Rewritten to: `http://api-service:8080/users`
- Backend receives: `/users` (not `/api/users`)

### 2. **Multiple Paths to Same Service**

```yaml
paths:
- path: /app
  pathType: Prefix
  backend:
    service:
      name: web-service
      port:
        number: 80
- path: /application
  pathType: Prefix
  backend:
    service:
      name: web-service
      port:
        number: 80
```

Both `/app/*` and `/application/*` route to the same service.

### 3. **Multiple Services on Same Host**

```yaml
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8080
      - path: /images
        pathType: Prefix
        backend:
          service:
            name: cdn-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

**Path Evaluation Order (Most Specific First):**
1. `/api/*` → `backend-service`
2. `/images/*` → `cdn-service`
3. `/*` (everything else) → `frontend-service`

### 4. **Wildcard Hosts**

```yaml
spec:
  rules:
  - host: "*.example.com"
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: wildcard-service
            port:
              number: 80
```

Matches:
- `app.example.com` ✅
- `api.example.com` ✅
- `staging.example.com` ✅

Does NOT match:
- `example.com` ❌ (no subdomain)
- `app.staging.example.com` ❌ (too many levels)

---

## Debugging Ingress Path Issues

### 1. **Check Ingress Configuration**

```bash
# View Ingress details
kubectl describe ingress web-ingress -n k8squest

# Check path configuration
kubectl get ingress web-ingress -n k8squest -o yaml
```

Look for:
- `spec.rules[].http.paths[].path` - Is it correct?
- `spec.rules[].http.paths[].pathType` - Prefix, Exact, or ImplementationSpecific?
- `spec.rules[].http.paths[].backend` - Does it point to the right service?

### 2. **Test Path Matching Locally**

```bash
# Add host to /etc/hosts
echo "127.0.0.1 myapp.local" | sudo tee -a /etc/hosts

# Test different paths
curl -v http://myapp.local/
curl -v http://myapp.local/api
curl -v http://myapp.local/api/users
```

Look for:
- **200 OK** - Path matches, request succeeded
- **404 Not Found** - Path doesn't match OR resource doesn't exist
- **503 Service Unavailable** - Path matches but backend is down

### 3. **Check Ingress Controller Logs**

```bash
# Find Ingress controller pod (varies by installation)
kubectl get pods -n ingress-nginx

# View logs
kubectl logs -n ingress-nginx ingress-nginx-controller-xxxxx

# Follow logs in real-time
kubectl logs -n ingress-nginx ingress-nginx-controller-xxxxx -f
```

Look for:
```
# Path matched successfully
"GET / HTTP/1.1" 200

# Path didn't match any rule
"GET /api HTTP/1.1" 404

# Backend service unavailable
"GET / HTTP/1.1" 503
```

### 4. **Verify Backend Service**

```bash
# Check service exists
kubectl get service web-service -n k8squest

# Check service has endpoints
kubectl get endpoints web-service -n k8squest

# Describe service
kubectl describe service web-service -n k8squest
```

If endpoints are empty, the service selector might not match any pods.

### 5. **Test Service Directly**

```bash
# Port-forward to service
kubectl port-forward -n k8squest service/web-service 8080:80

# Test in another terminal
curl http://localhost:8080/
```

This bypasses the Ingress to test if the backend service works.

---

## Best Practices for Ingress Paths

### 1. **Use Specific Paths First, General Paths Last**

```yaml
# ✅ GOOD: Most specific first
paths:
- path: /api/v2
  pathType: Prefix
  backend:
    service:
      name: api-v2-service
- path: /api
  pathType: Prefix
  backend:
    service:
      name: api-v1-service
- path: /
  pathType: Prefix
  backend:
    service:
      name: frontend-service
```

```yaml
# ❌ BAD: General path catches everything
paths:
- path: /
  pathType: Prefix
  backend:
    service:
      name: frontend-service
- path: /api        # Never reached! "/" already matched
  pathType: Prefix
  backend:
    service:
      name: api-service
```

### 2. **Be Careful with Trailing Slashes**

```yaml
# With Exact pathType
path: /login
pathType: Exact

# Matches: /login
# Does NOT match: /login/ (has trailing slash!)
```

For `Exact` paths, `/login` and `/login/` are DIFFERENT.

**Recommendation:** Use `Prefix` unless you have a specific reason to use `Exact`.

### 3. **Document Your Routing Logic**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    description: "Routes traffic for example.com application"
spec:
  rules:
  - host: example.com
    http:
      paths:
      # API v2 (current)
      - path: /api/v2
        pathType: Prefix
        backend:
          service:
            name: api-v2-service
            port:
              number: 8080
      
      # API v1 (deprecated, remove after Q2 2024)
      - path: /api/v1
        pathType: Prefix
        backend:
          service:
            name: api-v1-service
            port:
              number: 8080
      
      # Static assets (CDN)
      - path: /static
        pathType: Prefix
        backend:
          service:
            name: cdn-service
            port:
              number: 80
      
      # Frontend (catch-all)
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

### 4. **Test Path Changes Before Production**

```bash
# Create test Ingress with different host
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-ingress
  namespace: k8squest
spec:
  rules:
  - host: test.myapp.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
EOF

# Test with curl
curl http://test.myapp.local/

# If it works, apply to production Ingress
```

### 5. **Monitor 404 Rates**

Set up monitoring/alerting for 404 errors:

```yaml
# Prometheus alert example
groups:
- name: ingress_alerts
  rules:
  - alert: HighIngress404Rate
    expr: |
      sum(rate(nginx_ingress_controller_requests{status="404"}[5m])) 
      / 
      sum(rate(nginx_ingress_controller_requests[5m])) > 0.05
    for: 5m
    annotations:
      summary: "High 404 rate on Ingress (>5% of requests)"
      description: "Check for path misconfigurations or broken links"
```

### 6. **Use Path Aliases for Backward Compatibility**

```yaml
# Support both /api and /v1/api during migration
paths:
- path: /v1/api
  pathType: Prefix
  backend:
    service:
      name: api-service
      port:
        number: 8080
- path: /api
  pathType: Prefix
  backend:
    service:
      name: api-service
      port:
        number: 8080
```

---

## Key Takeaways

1. **Path Matching is Literal:**
   - `/api` does NOT match `/`
   - `/` DOES match everything (with Prefix pathType)
   - Order matters when using multiple paths

2. **Choose the Right PathType:**
   - **Prefix:** Most common, matches path prefixes (e.g., `/api` matches `/api/users`)
   - **Exact:** Matches only exact path (e.g., `/login` matches `/login` only)
   - **ImplementationSpecific:** Depends on Ingress controller, avoid unless necessary

3. **Test Your Paths:**
   - Use `curl` to test different paths
   - Check Ingress controller logs
   - Verify service endpoints exist

4. **Path Order Matters:**
   - Most specific paths first
   - General catch-all paths last
   - `/` should almost always be last

5. **Common Mistakes:**
   - Using `/api` when app serves at `/`
   - Using `Exact` when you need `Prefix`
   - Putting catch-all `/` path first (it catches everything!)
   - Forgetting trailing slashes with `Exact` pathType

6. **Real-World Lessons:**
   - Path misconfigurations can cause complete outages
   - Test ALL API versions, not just one
   - Monitor 404 rates to catch routing issues
   - Have rollback procedures for Ingress changes

---

## What's Next?

You've mastered Ingress path-based routing! You now understand:
- ✅ How Kubernetes Ingress routes HTTP traffic
- ✅ The difference between Prefix, Exact, and ImplementationSpecific pathTypes
- ✅ How to debug path mismatch issues
- ✅ Best practices for configuring Ingress paths

In the next levels, you'll explore more advanced networking concepts like NetworkPolicy for controlling traffic between pods, session affinity for stateful applications, and cross-namespace service communication.

**Continue your K8sQuest journey to unlock the next challenge!** 🚀

---

## Additional Resources

- [Kubernetes Ingress Documentation](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [Ingress Path Matching](https://kubernetes.io/docs/concepts/services-networking/ingress/#path-types)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Ingress Path Rewriting](https://kubernetes.github.io/ingress-nginx/examples/rewrite/)

---

**Mission Complete!** 🎉  
You've earned 250 XP and leveled up your Kubernetes networking skills!
