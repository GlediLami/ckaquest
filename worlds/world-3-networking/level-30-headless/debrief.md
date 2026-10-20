# 🎯 Level 30 Debrief: Headless Services & StatefulSet DNS

**Congratulations!** You've completed World 3: Networking & Services by mastering headless services and StatefulSet DNS! This is one of the most important patterns for running stateful applications in Kubernetes, and understanding it will enable you to deploy databases, message queues, and distributed systems with confidence.

---

## 📊 What You Just Fixed

### The Problem
Your StatefulSet pods couldn't communicate with each other using predictable DNS names, causing:
- **Pods unable to discover peers** in the cluster
- **Database replication failing** (can't find master/slave nodes)
- **Distributed systems broken** (peers can't coordinate)
- **Random pod assignment** instead of specific pod targeting

### The Root Cause
```yaml
# ❌ BROKEN: Regular ClusterIP service
apiVersion: v1
kind: Service
metadata:
  name: web-cluster
spec:
  clusterIP: 10.96.100.50  # ❌ Has virtual IP (not headless)
  selector:
    app: web-cluster
  ports:
  - port: 80
```

**Why this fails for StatefulSets:**
1. Regular ClusterIP service gets a virtual IP (10.96.100.50)
2. DNS resolves service name to this virtual IP
3. Traffic is load-balanced to random pods
4. **Per-pod DNS names don't work** (web-0.web-cluster returns NXDOMAIN)
5. StatefulSet pods can't find each other by name
6. Applications expecting stable pod identities fail

### The Solution
```yaml
# ✅ FIXED: Headless service
apiVersion: v1
kind: Service
metadata:
  name: web-cluster
spec:
  clusterIP: None  # ✅ No virtual IP (headless)
  selector:
    app: web-cluster
  ports:
  - port: 80
```

**How this works:**
1. Service has `clusterIP: None` (headless)
2. No virtual IP is assigned
3. DNS returns pod IPs directly
4. **Per-pod DNS names work!** (web-0.web-cluster → web-0's IP)
5. Each pod has a stable network identity
6. Pods can find each other by predictable names

**DNS Resolution:**
```
# Headless service DNS:
web-0.web-cluster.k8squest.svc.cluster.local → 10.244.1.5 (web-0 pod)
web-1.web-cluster.k8squest.svc.cluster.local → 10.244.1.6 (web-1 pod)
web-2.web-cluster.k8squest.svc.cluster.local → 10.244.1.7 (web-2 pod)

# Service DNS (returns all pod IPs):
web-cluster.k8squest.svc.cluster.local → [10.244.1.5, 10.244.1.6, 10.244.1.7]
```

---

## 🔍 Deep Dive: Headless Services

### What is a Headless Service?

A headless service is a Kubernetes Service without a ClusterIP (virtual IP address). Instead of load balancing traffic to pods, it provides direct DNS entries for each pod.

**Definition:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  clusterIP: None  # ← This makes it "headless"
  selector:
    app: my-app
  ports:
  - port: 80
```

**Key Characteristic:** `clusterIP: None`

### Regular Service vs Headless Service

#### Regular ClusterIP Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  clusterIP: 10.96.50.100  # Virtual IP assigned
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
```

**Behavior:**
```
┌────────────────────────────────────────────────┐
│ Client queries:                                 │
│   web-service.default.svc.cluster.local        │
│           ↓                                     │
│   DNS returns: 10.96.50.100 (ClusterIP)       │
│           ↓                                     │
│   kube-proxy load balances to pods:            │
│   ┌──────────┬──────────┬──────────┐          │
│   │ Pod A    │ Pod B    │ Pod C    │          │
│   │10.1.1.5  │10.1.1.6  │10.1.1.7  │          │
│   └──────────┴──────────┴──────────┘          │
│                                                 │
│ Features:                                       │
│ ✅ Single virtual IP                           │
│ ✅ Load balancing                              │
│ ✅ Service discovery                           │
│ ❌ No per-pod DNS                              │
│ ❌ Cannot target specific pod                  │
└────────────────────────────────────────────────┘
```

#### Headless Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  clusterIP: None  # ← Headless!
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
```

**Behavior:**
```
┌────────────────────────────────────────────────┐
│ Client queries:                                 │
│   web-service.default.svc.cluster.local        │
│           ↓                                     │
│   DNS returns ALL pod IPs (A records):         │
│   [10.1.1.5, 10.1.1.6, 10.1.1.7]              │
│   (no load balancing, client chooses)          │
│                                                 │
│ Per-pod DNS also works:                        │
│   pod-0.web-service → 10.1.1.5                │
│   pod-1.web-service → 10.1.1.6                │
│   pod-2.web-service → 10.1.1.7                │
│           ↓                                     │
│   ┌──────────┬──────────┬──────────┐          │
│   │ Pod 0    │ Pod 1    │ Pod 2    │          │
│   │10.1.1.5  │10.1.1.6  │10.1.1.7  │          │
│   └──────────┴──────────┴──────────┘          │
│                                                 │
│ Features:                                       │
│ ❌ No virtual IP                               │
│ ❌ No load balancing                           │
│ ✅ Service discovery                           │
│ ✅ Per-pod DNS names                           │
│ ✅ Direct pod targeting                        │
└────────────────────────────────────────────────┘
```

### Comparison Table

| Feature | Regular Service | Headless Service |
|---------|----------------|------------------|
| **ClusterIP value** | IP address (e.g., 10.96.50.100) | None |
| **Virtual IP** | ✅ Yes | ❌ No |
| **Load balancing** | ✅ Yes (kube-proxy) | ❌ No |
| **Service DNS** | Returns ClusterIP | Returns all pod IPs |
| **Per-pod DNS** | ❌ No | ✅ Yes |
| **kube-proxy rules** | ✅ Created | ❌ Not created |
| **Best for** | Deployments (stateless) | StatefulSets (stateful) |
| **Use case** | Web servers, APIs | Databases, clusters |

---

## 🎯 StatefulSet DNS Convention

### DNS Naming Format

For a StatefulSet with headless service:

```
<pod-name>.<service-name>.<namespace>.svc.<cluster-domain>
```

**Example:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
  namespace: production
spec:
  clusterIP: None
  
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
  namespace: production
spec:
  serviceName: mysql-service
  replicas: 3
```

**DNS Names:**
```
# Full DNS names:
mysql-0.mysql-service.production.svc.cluster.local
mysql-1.mysql-service.production.svc.cluster.local
mysql-2.mysql-service.production.svc.cluster.local

# Short names (within same namespace):
mysql-0.mysql-service
mysql-1.mysql-service
mysql-2.mysql-service

# Service DNS (returns all pod IPs):
mysql-service.production.svc.cluster.local
```

### How DNS Resolution Works

1. **Pod gets name from StatefulSet:**
   - StatefulSet `mysql` with 3 replicas
   - Pods: `mysql-0`, `mysql-1`, `mysql-2`

2. **Service provides domain:**
   - Service name: `mysql-service`
   - Domain: `mysql-service.production.svc.cluster.local`

3. **Kubernetes DNS creates per-pod A records:**
   ```
   mysql-0.mysql-service.production.svc.cluster.local → 10.244.1.5
   mysql-1.mysql-service.production.svc.cluster.local → 10.244.1.6
   mysql-2.mysql-service.production.svc.cluster.local → 10.244.1.7
   ```

4. **Service DNS returns all pods:**
   ```
   mysql-service.production.svc.cluster.local → [10.244.1.5, 10.244.1.6, 10.244.1.7]
   ```

### Testing DNS Resolution

```bash
# Deploy a debug pod
kubectl run -it --rm debug --image=busybox:1.28 -- sh

# Test per-pod DNS
nslookup mysql-0.mysql-service.production.svc.cluster.local
# Returns: 10.244.1.5

# Test service DNS
nslookup mysql-service.production.svc.cluster.local
# Returns: 10.244.1.5, 10.244.1.6, 10.244.1.7

# Test from application
ping mysql-0.mysql-service
# Works! (short name within same namespace)
```

---

## 💔 Real-World Horror Story: The $3.2M MongoDB Migration Disaster

**Company:** DataFlow Inc. (Analytics platform)  
**Date:** August 2023  
**Duration:** 8 hours of downtime + 3 days of data inconsistency  
**Impact:** $3.2M in lost revenue + major customer exodus

### The Setup
DataFlow was migrating their MongoDB cluster to Kubernetes:
- **3-node MongoDB replica set** (1 primary, 2 secondaries)
- **500GB of customer analytics data**
- **$40M annual revenue** depending on this database
- Black Friday preparation (migration scheduled 2 months before)

### The Architecture (Attempted)

```yaml
# ❌ BROKEN: Regular ClusterIP service (not headless!)
apiVersion: v1
kind: Service
metadata:
  name: mongodb
spec:
  # ❌ MISSING: clusterIP: None
  selector:
    app: mongodb
  ports:
  - port: 27017

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
spec:
  serviceName: mongodb
  replicas: 3
  template:
    spec:
      containers:
      - name: mongodb
        image: mongo:5.0
        command:
        - mongod
        - --replSet=rs0
        - --bind_ip_all
```

**The Fatal Mistake:** No `clusterIP: None` in the service!

### The Incident Timeline

**Friday, 2:00 AM - Migration Begins**
- Team deploys MongoDB StatefulSet
- Pods start: mongodb-0, mongodb-1, mongodb-2
- All pods healthy

**2:15 AM - Initialize Replica Set**
```javascript
// Engineer connects to mongodb-0
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongodb-0.mongodb:27017" },
    { _id: 1, host: "mongodb-1.mongodb:27017" },
    { _id: 2, host: "mongodb-2.mongodb:27017" }
  ]
})
```

**Output:**
```javascript
{
  "ok": 0,
  "errmsg": "Couldn't resolve host mongodb-0.mongodb",
  "code": 14
}
```

❌ **Per-pod DNS doesn't work! Service is not headless!**

**2:20 AM - Workaround Attempt #1: Use Pod IPs**
```javascript
// Engineer tries with pod IPs directly
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "10.244.1.5:27017" },  // mongodb-0 IP
    { _id: 1, host: "10.244.1.6:27017" },  // mongodb-1 IP
    { _id: 2, host: "10.244.1.7:27017" }   // mongodb-2 IP
  ]
})
// Success: { "ok": 1 }
```

✅ **Replica set initialized!** Team celebrates.

**2:30 AM - Data Migration Starts**
- Begin copying 500GB from old database
- Estimated time: 4 hours

**6:45 AM - Migration 95% Complete**
- 475GB transferred
- Only 25GB remaining
- Team takes coffee break

**6:52 AM - Kubernetes Reschedules Pod**
- Node running mongodb-1 gets drained for maintenance
- Pod mongodb-1 terminated
- New mongodb-1 pod starts on different node
- **New IP: 10.244.2.8** (was 10.244.1.6)

**6:53 AM - Replica Set Breaks**
```
# MongoDB log on mongodb-0 (primary):
2023-08-11T06:53:12.345 E REPL [replication] cannot connect to
  10.244.1.6:27017 (mongodb-1): Connection refused
2023-08-11T06:53:12.456 W REPL [replication] member 10.244.1.6:27017
  is down
```

**The problem:**
- Replica set configured with OLD IP: 10.244.1.6
- New pod has NEW IP: 10.244.2.8
- Primary can't reach secondary
- **Replica set loses quorum!**

**6:55 AM - Write Failures Begin**
```
# Application errors:
MongoError: not master and slaveOk=false
```

- Primary demoted itself (lost majority)
- No new primary elected (only 1 of 3 members reachable)
- **All writes failing!**
- Customers see error pages

**7:00 AM - Panic Sets In**
- On-call engineer woken up
- Production database down
- Black Friday traffic starting in 3 months
- Management escalates to VP level

**7:15 AM - Realization**
Senior engineer joins war room:
```bash
# Check service
kubectl get service mongodb

# Output:
NAME      TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)     AGE
mongodb   ClusterIP   10.96.100.50    <none>        27017/TCP   5h

# CLUSTER-IP should be "None"!
```

**Root cause discovered: Service is not headless!**

**7:20 AM - Emergency Fix Applied**
```yaml
# Patch service to be headless
kubectl patch service mongodb -p '{"spec":{"clusterIP":"None"}}'

# ERROR: Cannot change ClusterIP on existing service!
```

Can't patch! Must delete and recreate!

**7:25 AM - The Risky Fix**
```bash
# Delete service (risky!)
kubectl delete service mongodb

# Create headless service
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: mongodb
spec:
  clusterIP: None  # ✅ HEADLESS!
  selector:
    app: mongodb
  ports:
  - port: 27017
EOF
```

**7:30 AM - Reconfigure Replica Set**
```javascript
// Connect to mongodb-0
use admin

// Get current config
cfg = rs.conf()

// Update to use DNS names instead of IPs
cfg.members[0].host = "mongodb-0.mongodb:27017"
cfg.members[1].host = "mongodb-1.mongodb:27017"
cfg.members[2].host = "mongodb-2.mongodb:27017"

// Reconfigure
rs.reconfig(cfg)
```

**7:35 AM - Replica Set Recovers**
```
# New replica set status:
rs0:PRIMARY> rs.status()
{
  members: [
    { name: "mongodb-0.mongodb:27017", stateStr: "PRIMARY" },
    { name: "mongodb-1.mongodb:27017", stateStr: "SECONDARY" },
    { name: "mongodb-2.mongodb:27017", stateStr: "SECONDARY" }
  ]
}
```

✅ **Replica set healthy!**

**7:40 AM - Data Inconsistency Discovered**
```bash
# Check data on each replica
db.analytics.count()  # mongodb-0: 12,450,382
db.analytics.count()  # mongodb-1: 12,449,201  (1,181 docs behind)
db.analytics.count()  # mongodb-2: 12,448,905  (1,477 docs behind)
```

**Problem:** During the 45-minute outage, some writes succeeded on primary but weren't replicated!

**7:45 AM - Rollback Decision**
- Data inconsistency unacceptable
- Must restore from backup
- Lose 5 hours of data

**8:00 AM - Restore from Backup**
```bash
# Restore from 1:30 AM backup (before migration)
# Lose all data from 1:30 AM - 7:45 AM (6 hours 15 minutes)
```

**10:00 AM - Service Restored**
- Database back online
- Lost 6+ hours of analytics data
- Customers notified of data loss

### The Damage

**Financial:**
- **$3.2M in lost revenue** (8 hours downtime during peak hours)
- **$400K in customer refunds** (analytics data lost)
- **$150K emergency contractor fees** (data recovery specialists)
- **Total: $3.75M**

**Operational:**
- **8 hours of complete downtime**
- **6 hours of data lost** (analytics for 15,000 customers)
- **250 support tickets** filed
- **45 enterprise customers** lost trust

**Reputational:**
- **3 major customers** cancelled contracts (total $2M ARR)
- **Press coverage** of the outage
- **Stock price dropped** 8% on news

### Root Cause Analysis

**Immediate Cause:**
- Service not configured as headless (`clusterIP: None`)
- MongoDB replica set used pod IPs instead of DNS names
- Pod rescheduling changed IP, breaking replica set

**Contributing Factors:**

1. **Insufficient Testing:**
   - Never tested pod rescheduling in staging
   - Didn't validate per-pod DNS before production
   - No chaos engineering (pod deletion tests)

2. **Lack of Knowledge:**
   - Team didn't know about headless services
   - Used pod IPs thinking it was "more reliable"
   - Didn't read StatefulSet documentation thoroughly

3. **No Validation:**
   - No automated check that service was headless
   - No DNS tests before declaring migration complete
   - Manual configuration prone to errors

4. **Poor Runbook:**
   - No procedure for StatefulSet deployments
   - No checklist for headless service requirements
   - Engineers learning on the fly

### What Should Have Been Done

**Correct Configuration:**
```yaml
# ✅ CORRECT: Headless service
apiVersion: v1
kind: Service
metadata:
  name: mongodb
spec:
  clusterIP: None  # ← CRITICAL for StatefulSets!
  selector:
    app: mongodb
  ports:
  - port: 27017
  - port: 27018  # Optional: direct pod access

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
spec:
  serviceName: mongodb  # Must match headless service name
  replicas: 3
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:5.0
        command:
        - mongod
        - --replSet=rs0
        - --bind_ip_all
        env:
        # Use DNS names, not IPs!
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
```

**Initialization Script:**
```javascript
// ✅ Use DNS names (survive pod rescheduling)
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongodb-0.mongodb:27017" },  // ✅ DNS name
    { _id: 1, host: "mongodb-1.mongodb:27017" },  // ✅ DNS name
    { _id: 2, host: "mongodb-2.mongodb:27017" }   // ✅ DNS name
  ]
})

// ❌ NEVER use pod IPs!
// They change when pods reschedule!
```

**Validation Tests:**
```bash
# Test 1: Verify service is headless
kubectl get service mongodb -o jsonpath='{.spec.clusterIP}'
# Must output: None

# Test 2: Verify per-pod DNS works
kubectl run -it --rm debug --image=busybox:1.28 -- \
  nslookup mongodb-0.mongodb
# Must resolve to pod IP

# Test 3: Test pod rescheduling (chaos engineering)
kubectl delete pod mongodb-1
# Wait for pod to reschedule
# Verify replica set still healthy
# Verify new pod IP doesn't break anything
```

### Lessons Learned

1. **Always use headless services for StatefulSets**
   ```yaml
   spec:
     clusterIP: None  # Non-negotiable!
   ```

2. **Never use pod IPs in application configuration**
   - Pod IPs change on rescheduling
   - Always use DNS names
   - DNS names are stable

3. **Test pod rescheduling before production**
   ```bash
   # Simulate pod failure
   kubectl delete pod mongodb-1
   # Verify application still works
   ```

4. **Automate validation**
   ```bash
   # Pre-deployment check
   if [[ $(kubectl get svc mongodb -o jsonpath='{.spec.clusterIP}') != "None" ]]; then
     echo "ERROR: Service must be headless!"
     exit 1
   fi
   ```

5. **Document StatefulSet requirements**
   - Checklist for headless services
   - Runbook for common issues
   - Training for all engineers

### Post-Incident Improvements

**1. Pre-flight Checks:**
```bash
#!/bin/bash
# validate-statefulset.sh

echo "Validating StatefulSet deployment..."

# Check 1: Service is headless
SVC_NAME="$1"
CLUSTER_IP=$(kubectl get svc "$SVC_NAME" -o jsonpath='{.spec.clusterIP}')
if [[ "$CLUSTER_IP" != "None" ]]; then
  echo "❌ FAIL: Service $SVC_NAME is not headless (clusterIP: $CLUSTER_IP)"
  exit 1
fi
echo "✅ Service is headless"

# Check 2: StatefulSet references correct service
SS_NAME="$2"
SVC_NAME_IN_SS=$(kubectl get statefulset "$SS_NAME" -o jsonpath='{.spec.serviceName}')
if [[ "$SVC_NAME_IN_SS" != "$SVC_NAME" ]]; then
  echo "❌ FAIL: StatefulSet serviceName mismatch"
  exit 1
fi
echo "✅ StatefulSet references correct service"

# Check 3: Per-pod DNS works
for i in $(seq 0 2); do
  POD_NAME="${SS_NAME}-${i}"
  DNS_NAME="${POD_NAME}.${SVC_NAME}"
  
  kubectl run dns-test --image=busybox:1.28 --rm -it --restart=Never -- \
    nslookup "$DNS_NAME" &>/dev/null
  
  if [[ $? -ne 0 ]]; then
    echo "❌ FAIL: DNS resolution failed for $DNS_NAME"
    exit 1
  fi
  echo "✅ DNS works for $DNS_NAME"
done

echo "✅ All checks passed!"
```

**2. Chaos Engineering:**
```bash
# Test pod rescheduling regularly
while true; do
  # Delete random replica
  POD=$(kubectl get pods -l app=mongodb -o name | shuf -n1)
  kubectl delete "$POD"
  
  # Wait for recovery
  kubectl wait --for=condition=Ready "$POD" --timeout=60s
  
  # Verify replica set health
  kubectl exec mongodb-0 -- mongosh --eval "rs.status()"
  
  sleep 300  # 5 minutes
done
```

**3. Policy Enforcement:**
```yaml
# OPA policy: Require headless service for StatefulSets
package kubernetes.admission

deny[msg] {
  input.request.kind.kind == "StatefulSet"
  svc_name := input.request.object.spec.serviceName
  
  svc := data.kubernetes.services[svc_name]
  svc.spec.clusterIP != "None"
  
  msg := sprintf("StatefulSet %s requires headless service (clusterIP: None), but service %s has clusterIP: %s",
    [input.request.object.metadata.name, svc_name, svc.spec.clusterIP])
}
```

---

## 📚 Common Use Cases for Headless Services

### 1. Database Clusters

**MongoDB Replica Set:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mongo
spec:
  clusterIP: None
  selector:
    app: mongo
  ports:
  - port: 27017

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongo
spec:
  serviceName: mongo
  replicas: 3
  template:
    spec:
      containers:
      - name: mongo
        image: mongo:5.0
        command:
        - mongod
        - --replSet=rs0
```

**Initialize:**
```javascript
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo-0.mongo:27017" },
    { _id: 1, host: "mongo-1.mongo:27017" },
    { _id: 2, host: "mongo-2.mongo:27017" }
  ]
})
```

**MySQL Master-Slave:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  clusterIP: None
  selector:
    app: mysql
  ports:
  - port: 3306

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  template:
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_MASTER_HOST
          value: mysql-0.mysql  # ✅ Stable DNS for master
```

### 2. Message Queues

**Kafka Cluster:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: kafka
spec:
  clusterIP: None
  selector:
    app: kafka
  ports:
  - port: 9092

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: kafka
spec:
  serviceName: kafka
  replicas: 3
  template:
    spec:
      containers:
      - name: kafka
        image: confluentinc/cp-kafka:latest
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: KAFKA_ADVERTISED_LISTENERS
          value: PLAINTEXT://$(POD_NAME).kafka:9092
        - name: KAFKA_ZOOKEEPER_CONNECT
          value: zk-0.zk:2181,zk-1.zk:2181,zk-2.zk:2181
```

**RabbitMQ Cluster:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: rabbitmq
spec:
  clusterIP: None
  selector:
    app: rabbitmq
  ports:
  - name: amqp
    port: 5672
  - name: management
    port: 15672

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: rabbitmq
spec:
  serviceName: rabbitmq
  replicas: 3
  template:
    spec:
      containers:
      - name: rabbitmq
        image: rabbitmq:3.9-management
        env:
        - name: RABBITMQ_DEFAULT_USER
          value: admin
        - name: RABBITMQ_ERLANG_COOKIE
          value: secret-cookie
```

### 3. Distributed Systems

**etcd Cluster:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: etcd
spec:
  clusterIP: None
  selector:
    app: etcd
  ports:
  - name: client
    port: 2379
  - name: peer
    port: 2380

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: etcd
spec:
  serviceName: etcd
  replicas: 3
  template:
    spec:
      containers:
      - name: etcd
        image: quay.io/coreos/etcd:v3.5
        command:
        - etcd
        - --name=$(POD_NAME)
        - --initial-advertise-peer-urls=http://$(POD_NAME).etcd:2380
        - --advertise-client-urls=http://$(POD_NAME).etcd:2379
        - --initial-cluster=etcd-0=http://etcd-0.etcd:2380,etcd-1=http://etcd-1.etcd:2380,etcd-2=http://etcd-2.etcd:2380
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
```

**Zookeeper Ensemble:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: zk
spec:
  clusterIP: None
  selector:
    app: zk
  ports:
  - name: client
    port: 2181
  - name: follower
    port: 2888
  - name: election
    port: 3888

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: zk
spec:
  serviceName: zk
  replicas: 3
  template:
    spec:
      containers:
      - name: zk
        image: zookeeper:3.7
        env:
        - name: ZOO_SERVERS
          value: server.1=zk-0.zk:2888:3888;2181 server.2=zk-1.zk:2888:3888;2181 server.3=zk-2.zk:2888:3888;2181
```

---

## 🎯 Best Practices

### 1. Always Use Headless Services for StatefulSets

```yaml
# ✅ DO THIS:
apiVersion: v1
kind: Service
metadata:
  name: my-statefulset-svc
spec:
  clusterIP: None  # Always for StatefulSets!
  selector:
    app: my-app

# ❌ NOT THIS:
spec:
  # clusterIP: 10.96.100.50  # Wrong for StatefulSets!
```

### 2. Use DNS Names, Never Pod IPs

```javascript
// ✅ DO THIS:
rs.initiate({
  members: [
    { host: "mongo-0.mongo:27017" },  // DNS name
    { host: "mongo-1.mongo:27017" },
    { host: "mongo-2.mongo:27017" }
  ]
})

// ❌ NOT THIS:
rs.initiate({
  members: [
    { host: "10.244.1.5:27017" },  // IP changes on reschedule!
    { host: "10.244.1.6:27017" },
    { host: "10.244.1.7:27017" }
  ]
})
```

### 3. Match serviceName in StatefulSet

```yaml
apiVersion: v1
kind: Service
metadata:
  name: database  # ← Service name

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: db
spec:
  serviceName: database  # ← Must match service name!
```

### 4. Test Per-Pod DNS Before Production

```bash
# Validation script
for i in 0 1 2; do
  kubectl run dns-test --rm -it --image=busybox:1.28 -- \
    nslookup my-app-$i.my-service
done
```

### 5. Combine Headless + Regular Services

```yaml
# Headless service for StatefulSet (per-pod DNS)
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
spec:
  clusterIP: None
  selector:
    app: mysql

---
# Regular service for read traffic (load balanced)
apiVersion: v1
kind: Service
metadata:
  name: mysql-read
spec:
  selector:
    app: mysql
  ports:
  - port: 3306

# Usage:
# Write to master: mysql-0.mysql-headless:3306
# Read from any replica: mysql-read:3306 (load balanced)
```

### 6. Use Init Containers for DNS Verification

```yaml
apiVersion: apps/v1
kind: StatefulSet
spec:
  template:
    spec:
      initContainers:
      - name: verify-dns
        image: busybox:1.28
        command:
        - sh
        - -c
        - |
          # Wait for DNS to be ready
          until nslookup $(hostname).my-service; do
            echo "Waiting for DNS..."
            sleep 2
          done
          echo "DNS is ready!"
```

### 7. Monitor DNS Resolution

```yaml
# Prometheus ServiceMonitor for DNS health
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: dns-health
spec:
  selector:
    matchLabels:
      app: my-statefulset
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
```

---

## 🛠️ Troubleshooting Guide

### Problem 1: "Cannot resolve pod DNS name"

**Symptom:**
```bash
$ nslookup pod-0.my-service
Server:    10.96.0.10
Address 1: 10.96.0.10 kube-dns.kube-system.svc.cluster.local

nslookup: can't resolve 'pod-0.my-service': Name or service not known
```

**Diagnosis:**
```bash
# Check if service is headless
kubectl get service my-service -o yaml | grep clusterIP
```

**Solution:**
```bash
# Service must have clusterIP: None
kubectl delete service my-service
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  clusterIP: None  # ← Fix: Make it headless
  selector:
    app: my-app
EOF
```

### Problem 2: "DNS returns wrong pod IP"

**Symptom:**
```bash
$ nslookup pod-0.my-service
# Returns IP of pod-1 instead!
```

**Diagnosis:**
```bash
# Check StatefulSet serviceName
kubectl get statefulset my-app -o yaml | grep serviceName

# Check if names match
kubectl get service my-service
```

**Solution:**
```yaml
# StatefulSet serviceName must match Service name exactly
apiVersion: apps/v1
kind: StatefulSet
spec:
  serviceName: my-service  # ← Must match Service metadata.name
```

### Problem 3: "Service has ClusterIP, can't change to None"

**Symptom:**
```bash
$ kubectl patch service my-service -p '{"spec":{"clusterIP":"None"}}'
The Service "my-service" is invalid: spec.clusterIP: Invalid value: "None": field is immutable
```

**Solution:**
```bash
# Must delete and recreate (risky in production!)
kubectl delete service my-service
kubectl apply -f headless-service.yaml

# Or use blue-green deployment:
# 1. Create new headless service with different name
# 2. Update StatefulSet to use new service
# 3. Delete old service
```

### Problem 4: "Pods can't find each other after reschedule"

**Symptom:**
```
# MongoDB replica set member unreachable after pod reschedule
MongoError: no primary found in replica set
```

**Diagnosis:**
```bash
# Check if replica set uses IPs or DNS names
kubectl exec mongo-0 -- mongosh --eval "rs.conf()"
```

**Solution:**
```javascript
// Reconfigure to use DNS names
cfg = rs.conf()
cfg.members[0].host = "mongo-0.mongo:27017"  // DNS name
cfg.members[1].host = "mongo-1.mongo:27017"
cfg.members[2].host = "mongo-2.mongo:27017"
rs.reconfig(cfg)
```

---

## 🎓 Key Takeaways

### Must Remember

1. **Headless services have `clusterIP: None`** - No virtual IP, DNS returns pod IPs directly
2. **StatefulSets require headless services** - For stable per-pod DNS names
3. **DNS format: `pod-name.service-name.namespace.svc.cluster.local`**
4. **Never use pod IPs in config** - They change on reschedule, use DNS names
5. **Regular service returns random pod** - Headless service allows targeting specific pods

### StatefulSet + Headless Service Checklist

Before deploying to production:

- [ ] **Service has `clusterIP: None`**
- [ ] **StatefulSet `serviceName` matches Service name**
- [ ] **Application uses DNS names** (not pod IPs)
- [ ] **Tested per-pod DNS resolution**
- [ ] **Tested pod rescheduling** (delete pod, verify app still works)
- [ ] **Init containers verify DNS** before app starts
- [ ] **Monitoring on DNS resolution**
- [ ] **Runbook for common issues**

### Common Mistakes to Avoid

❌ **Forgetting `clusterIP: None`** - Service won't provide per-pod DNS  
❌ **Using pod IPs** - IPs change on reschedule, breaking apps  
❌ **Mismatched service names** - StatefulSet serviceName must match Service name  
❌ **Testing only once** - Test pod rescheduling, deletion, failures  
❌ **No validation** - Automate checks for headless service  
❌ **Assuming it works** - Verify DNS resolution before declaring success  

---

## 🏆 Achievement Unlocked!

**StatefulSet Master** - You can now:
- ✅ Configure headless services for StatefulSets
- ✅ Understand per-pod DNS naming conventions
- ✅ Deploy stateful applications (databases, message queues)
- ✅ Avoid the $3.2M MongoDB migration mistake
- ✅ Troubleshoot DNS and service issues

**World 3 Complete!** You've mastered Kubernetes networking and services:
- Service selectors and labels
- NodePort for external access
- DNS resolution and naming
- Ingress routing
- NetworkPolicy for traffic control
- Session affinity for stateful apps
- Cross-namespace communication
- Readiness probes and endpoints
- LoadBalancer vs NodePort
- Headless services for StatefulSets

---

## 🎯 What's Next?

You've completed **World 3: Networking & Services** (2,300 XP)!

### Continue Your Journey:
- **World 4: Storage & Persistence** (Coming soon)
- **World 5: Configuration & Secrets** (Coming soon)
- **World 6: Security & RBAC** (Coming soon)

### Further Learning:

- **Kubernetes Documentation:** [Headless Services](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services)
- **StatefulSets:** [StatefulSet Basics](https://kubernetes.io/docs/tutorials/stateful-application/basic-stateful-set/)
- **DNS for Services:** [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- **Real Examples:** [Running MongoDB on Kubernetes](https://www.mongodb.com/kubernetes)

---

*"Headless services are not missing a head—they're giving each pod its own identity."* - Kubernetes Wisdom

**Remember:** For StatefulSets, always use `clusterIP: None`. Your database cluster will thank you!

