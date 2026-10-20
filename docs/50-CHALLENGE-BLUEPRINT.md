# K8sQuest - 50 Challenge Blueprint


This document provides the complete reference for all 50 K8sQuest challenges across 5 worlds.

**Total Levels**: 50 
**Total XP**: 10,200  


## ✅ WORLD 1: CORE KUBERNETES BASICS (Levels 1-10) 

**Difficulty**: Beginner  
**Total XP**: 1,000


1. ✅ CrashLoopBackOff Challenge (100 XP)
2. ✅ Deployment Zero Replicas (100 XP)
3. ✅ ImagePullBackOff Mystery (100 XP)
4. ✅ Pending Pod Problem (100 XP)
5. ✅ Lost Connection - Labels & Selectors (100 XP)
6. ✅ Port Mismatch Mayhem (100 XP)
7. ✅ Sidecar Sabotage (100 XP)
8. ✅ Pod Logs Mystery (100 XP)
9. ✅ Init Container Gridlock (100 XP)
10. ✅ Namespace Confusion (100 XP)

---

## ✅ WORLD 2: DEPLOYMENTS & SCALING (Levels 11-20) 

**Difficulty**: Intermediate  
**Focus**: Deployment strategies, scaling, health checks  
**Total XP**: 1,350

### Level 11: Deployment Rollback Required
**Concept**: Failed rolling update due to bad image  
**Broken**: Deployment with new image that doesn't exist  
**Fix**: Rollback to previous version using `kubectl rollout undo`  
**XP**: 100 ✅

### Level 12: Rolling Update Stuck
**Concept**: RollingUpdate strategy misconfiguration  
**Broken**: maxSurge and maxUnavailable both zero  
**Fix**: Configure proper rolling update parameters  
**XP**: 150 ✅

### Level 13: Readiness Probe Blocking Traffic
**Concept**: Pod keeps restarting due to failed readiness probe  
**Broken**: Readiness probe checks wrong endpoint  
**Fix**: Update probe to check correct health endpoint  
**XP**: 150 ✅

### Level 14: Liveness Probe Causing Restarts
**Concept**: Liveness probe too aggressive causing restart loops  
**Broken**: Liveness probe with insufficient delay  
**Fix**: Add proper initialDelaySeconds and timeouts  
**XP**: 150 ✅

### Level 15: HPA Cannot Scale
**Concept**: HorizontalPodAutoscaler can't read metrics  
**Broken**: HPA without resource requests defined  
**Fix**: Set proper CPU/memory resource requests  
**XP**: 100 ✅

### Level 16: PodDisruptionBudget Too Restrictive
**Concept**: PDB blocks necessary maintenance  
**Broken**: PDB with minAvailable greater than replicas  
**Fix**: Set reasonable PDB (minAvailable ≤ replicas)  
**XP**: 200 ✅

### Level 17: Anti-Affinity Preventing Scheduling
**Concept**: Pod anti-affinity rules too strict  
**Broken**: Required anti-affinity with insufficient nodes  
**Fix**: Use preferred anti-affinity or add nodes  
**XP**: 200 ✅

### Level 18: Resource Requests Too High
**Concept**: Pods pending due to excessive resource requests  
**Broken**: Requests exceed available node capacity  
**Fix**: Reduce requests to realistic values  
**XP**: 150 ✅

### Level 19: Recreate Strategy Causing Downtime
**Concept**: Deployment strategy causes unnecessary downtime  
**Broken**: Recreate strategy instead of RollingUpdate  
**Fix**: Change to RollingUpdate strategy  
**XP**: 150 ✅

### Level 20: Deployment Selector Immutable
**Concept**: Attempted selector change blocks deployment  
**Broken**: Trying to update immutable selector field  
**Fix**: Delete and recreate deployment with new selector  
**XP**: 200 ✅

---

## ✅ WORLD 3: NETWORKING & SERVICES (Levels 21-30) 

**Difficulty**: Intermediate  
**Focus**: Services, Ingress, DNS, NetworkPolicy  
**Total XP**: 2,100

### Level 21: Service Selector Mismatch
**Concept**: Service can't find pods due to wrong selector  
**Broken**: Service selector doesn't match pod labels  
**Fix**: Fix selector to match pod labels correctly  
**XP**: 200 ✅

### Level 22: NodePort Out of Range
**Concept**: NodePort outside valid range  
**Broken**: NodePort set to invalid port number  
**Fix**: Use valid NodePort range (30000-32767)  
**XP**: 200 ✅

### Level 23: DNS Resolution Failure
**Concept**: Pod can't resolve service name  
**Broken**: Incorrect service name or DNS configuration  
**Fix**: Use correct FQDN or fix DNS policy  
**XP**: 250 ✅

### Level 24: Ingress Backend Not Found
**Concept**: Ingress routes to non-existent service  
**Broken**: Ingress backend service name typo  
**Fix**: Correct service name in ingress spec  
**XP**: 200 ✅

### Level 25: NetworkPolicy Blocking Traffic
**Concept**: NetworkPolicy denies all traffic  
**Broken**: Deny-all policy without allow rules  
**Fix**: Add proper ingress/egress rules  
**XP**: 250 ✅

### Level 26: Session Affinity Required
**Concept**: Stateful app needs sticky sessions  
**Broken**: Round-robin breaks user sessions  
**Fix**: Add `sessionAffinity: ClientIP` to service  
**XP**: 200 ✅

### Level 27: Cross-Namespace Communication Failed
**Concept**: Can't access service in different namespace  
**Broken**: Using short service name instead of FQDN  
**Fix**: Use `service.namespace.svc.cluster.local`  
**XP**: 200 ✅

### Level 28: Endpoints Empty
**Concept**: Service has no endpoints  
**Broken**: Pods not matching service selector  
**Fix**: Fix pod labels or service selector  
**XP**: 250 ✅

### Level 29: LoadBalancer Pending
**Concept**: LoadBalancer service stuck in pending  
**Broken**: Cloud provider not configured (local cluster)  
**Fix**: Use NodePort or install MetalLB  
**XP**: 250 ✅

### Level 30: Headless Service Misconfigured
**Concept**: StatefulSet needs headless service  
**Broken**: Regular ClusterIP instead of headless (clusterIP: None)  
**Fix**: Set clusterIP: None for headless service  
**XP**: 200 ✅

---

## ✅ WORLD 4: STORAGE & STATEFUL APPS (Levels 31-40) 

**Difficulty**: Advanced  
**Focus**: PersistentVolumes, StatefulSets, ConfigMaps, Secrets  
**Total XP**: 2,600

### Level 31: PVC Pending Forever
**Concept**: PersistentVolumeClaim can't find matching PV  
**Broken**: PVC requests storage but no PV available  
**Fix**: Create matching PV or use dynamic provisioning  
**XP**: 250 ✅

### Level 32: Volume Mount Path Error
**Concept**: Container can't access mounted volume  
**Broken**: Volume mounted to wrong path in container  
**Fix**: Correct volumeMount path in container spec  
**XP**: 250 ✅

### Level 33: Access Mode Mismatch
**Concept**: PVC and PV have incompatible access modes  
**Broken**: PVC wants ReadWriteMany but PV is ReadWriteOnce  
**Fix**: Match access modes between PVC and PV  
**XP**: 300 ✅

### Level 34: StatefulSet Volume Claim Issues
**Concept**: StatefulSet pod waiting for PVC  
**Broken**: VolumeClaimTemplate configuration error  
**Fix**: Fix volumeClaimTemplate spec  
**XP**: 300 ✅

### Level 35: StorageClass Not Found
**Concept**: PVC references non-existent StorageClass  
**Broken**: StorageClass name doesn't exist  
**Fix**: Use existing StorageClass or create new one  
**XP**: 250 ✅

### Level 36: ConfigMap Key Missing
**Concept**: Pod references non-existent ConfigMap key  
**Broken**: Container env references wrong key name  
**Fix**: Use correct ConfigMap key or add missing key  
**XP**: 250 ✅

### Level 37: Secret Encoding Wrong
**Concept**: Secret data not base64 encoded  
**Broken**: Plain text instead of base64  
**Fix**: Properly encode secret data or use stringData  
**XP**: 200 ✅

### Level 38: Volume Permission Denied
**Concept**: Container can't write to volume  
**Broken**: Volume has wrong permissions/ownership  
**Fix**: Add securityContext with proper fsGroup  
**XP**: 250 ✅

### Level 39: PV Reclaim Policy Delete
**Concept**: Data lost when PVC deleted  
**Broken**: PV has ReclaimPolicy: Delete  
**Fix**: Change to Retain or backup data  
**XP**: 300 ✅

### Level 40: EmptyDir vs PersistentVolume
**Concept**: Using emptyDir for persistent data  
**Broken**: Data lost on pod restart with emptyDir  
**Fix**: Replace emptyDir with PersistentVolumeClaim  
**XP**: 250 ✅

---

## ✅ WORLD 5: SECURITY & PRODUCTION OPS (Levels 41-50) 

**Difficulty**: Advanced/Expert  
**Focus**: RBAC, Security, Resource Management, Production Scenarios  
**Total XP**: 3,150

### Level 41: RBAC Permission Denied
**Concept**: ServiceAccount lacks necessary permissions  
**Broken**: Pod can't list/create resources due to missing RBAC  
**Fix**: Create proper Role and RoleBinding  
**XP**: 300 ✅

### Level 42: SecurityContext Privilege Escalation
**Concept**: Container running as root with privilege escalation  
**Broken**: SecurityContext allows root and privilege escalation  
**Fix**: Set runAsNonRoot, runAsUser, allowPrivilegeEscalation: false  
**XP**: 250 ✅

### Level 43: ResourceQuota Exceeded
**Concept**: Can't create pods, namespace quota exceeded  
**Broken**: ResourceQuota limits reached, pods pending  
**Fix**: Reduce resource requests or increase quota  
**XP**: 300 ✅

### Level 44: NetworkPolicy Blocking Database
**Concept**: NetworkPolicy blocks legitimate database traffic  
**Broken**: Strict NetworkPolicy denies necessary connections  
**Fix**: Add proper ingress/egress rules for database access  
**XP**: 350 ✅

### Level 45: Node Affinity Mismatch
**Concept**: Pod can't schedule due to node affinity rules  
**Broken**: Required affinity needs node label that doesn't exist  
**Fix**: Add label to node or use preferred affinity  
**XP**: 300 ✅

### Level 46: Taints and Tolerations
**Concept**: Pod rejected by node taints  
**Broken**: Node has taint, pod lacks matching toleration  
**Fix**: Add proper toleration to pod spec  
**XP**: 350 ✅

### Level 47: PodDisruptionBudget Violation
**Concept**: PDB prevents necessary pod eviction  
**Broken**: PDB minAvailable exceeds replica count  
**Fix**: Set realistic PDB (minAvailable ≤ replicas)  
**XP**: 300 ✅

### Level 48: Pod Security Standards
**Concept**: Pod violates restricted security standard  
**Broken**: Pod configuration doesn't meet security requirements  
**Fix**: Apply all restricted standard requirements  
**XP**: 350 ✅

### Level 49: PriorityClass Preemption
**Concept**: High-priority pods can't schedule  
**Broken**: Missing PriorityClass or wrong priority value  
**Fix**: Create and assign proper PriorityClass  
**XP**: 300 ✅

### Level 50: 🔥 CHAOS FINALE - The Perfect Storm
**Concept**: Complex production scenario with 9 simultaneous failures  
**Broken**: 
- RBAC: ServiceAccount exists but no Role/RoleBinding
- SecurityContext: Running as root with privilege escalation
- ResourceQuota: CPU quota exceeded (1 CPU but 3 replicas requesting 1 CPU each)
- NetworkPolicy: Deny-all policy blocking traffic
- Node Affinity: Configuration present but generic
- Taints/Tolerations: Missing tolerations for tainted nodes
- PodDisruptionBudget: minAvailable 5 but only 3 replicas
- Pod Security: Violates restricted standard
- PriorityClass: Not configured

**Fix**: Systematic debugging and resolution of ALL 9 issues:
1. Create Role and RoleBinding for RBAC
2. Configure proper SecurityContext (runAsNonRoot, no escalation)
3. Fix ResourceQuota and reduce replicas
4. Allow necessary traffic in NetworkPolicy
5. Configure node affinity appropriately
6. Add tolerations for tainted nodes
7. Set realistic PodDisruptionBudget
8. Meet Pod Security Standards (restricted)
9. Create and assign PriorityClass

**XP**: 500 ✅  
**Achievement**: 🏆 **Kubernetes Master** badge unlocked!

---

## 📁 Level Structure

Each level contains exactly 8 files:

```bash
worlds/world-X-name/level-Y-name/
├── mission.yaml       # Challenge metadata (level, title, XP, difficulty, concepts)
├── broken.yaml        # Intentionally broken K8s resources
├── solution.yaml      # Fixed configuration (reference solution)
├── validate.sh        # Executable validation script (pass/fail test)
├── hint-1.txt         # Initial observation hint
├── hint-2.txt         # Direction hint pointing toward solution
├── hint-3.txt         # Near-complete solution hint
└── debrief.md         # Comprehensive post-completion learning guide
```

### All Files Are Required
- **Total files per level**: 8
- **All validation scripts are executable**: `chmod +x validate.sh`

---

## 🎓 Learning Progression

### World 1: Foundation (Beginner)
Start here! Learn core debugging skills with pods, deployments, and basic troubleshooting.

### World 2: Deployment Mastery (Intermediate)
Master rolling updates, scaling, health probes, and deployment strategies.

### World 3: Network Ninja (Intermediate)
Understand services, DNS, ingress, and network policies for production apps.

### World 4: Storage Expert (Advanced)
Handle persistent volumes, StatefulSets, and configuration management.

### World 5: Production Ready (Advanced/Expert)
Apply security, RBAC, resource management, and handle complex multi-failure scenarios.

---

## 📊 XP Distribution

| World | Difficulty | Levels | Total XP | Avg XP/Level |
|-------|------------|--------|----------|--------------|
| 1     | Beginner   | 10     | 1,000    | 100          |
| 2     | Intermediate | 10   | 1,350    | 135          |
| 3     | Intermediate | 10   | 2,100    | 210          |
| 4     | Advanced   | 10     | 2,600    | 260          |
| 5     | Advanced   | 10     | 3,150    | 315          |
| **TOTAL** | **-**  | **50** | **10,200** | **204**  |

---

## 🏆 Completion Milestones

- **Level 10**: Complete World 1 - Kubernetes Basics Mastered
- **Level 20**: Complete World 2 - Deployment Expert
- **Level 30**: Complete World 3 - Networking Specialist
- **Level 40**: Complete World 4 - Storage & Config Pro
- **Level 50**: Complete World 5 - **🏆 Kubernetes Master**

**Final Achievement**: All 50 levels = 10,200 XP = Kubernetes Master Certification! 🎓

---

## 🚀 Usage Guide

### For Players
1. Start with `./play.sh`
2. Progress through worlds sequentially
3. Use hints when stuck (progressive unlocking)
4. Read debriefs after completion (key learning moments!)
5. Aim for 10,200 XP - become a Kubernetes Master!

### For Contributors
1. See [docs/contributing.md](contributing.md) for detailed guide
2. Each level requires all 8 files
3. Follow existing patterns from completed levels
4. Test thoroughly with validation scripts
5. Include real-world scenarios in debriefs
