# 🗺️ K8sQuest Learning Path

> **Your journey from Kubernetes beginner to production-ready engineer**

## 📊 Complete Skill Tree

```
K8sQuest Learning Path
│
├─ WORLD 1: Core Kubernetes Basics ⭐
│  │  Difficulty: Beginner | Time: 3-5 hours | XP: 1,450
│  │  
│  ├─ Level 1: CrashLoopBackOff (150 XP) ★ START HERE
│  │  Prerequisites: None
│  │  Skills: kubectl logs, pod debugging, exit codes
│  │  
│  ├─ Level 2: Deployment Basics (100 XP)
│  │  Prerequisites: Level 1
│  │  Skills: Deployments, rolling updates
│  │  
│  ├─ Level 3: ImagePullBackOff (100 XP)
│  │  Prerequisites: Level 1
│  │  Skills: Image management, registry auth
│  │  
│  ├─ Level 4: Pending Pod (100 XP)
│  │  Prerequisites: Level 1
│  │  Skills: Resource requests, scheduling
│  │  
│  ├─ Level 5: Label Selectors (150 XP)
│  │  Prerequisites: Level 1, 2
│  │  Skills: Labels, selectors, service discovery
│  │  
│  ├─ Level 6: Port Mismatches (150 XP)
│  │  Prerequisites: Level 5
│  │  Skills: Networking basics, port mapping
│  │  
│  ├─ Level 7: Multi-Container Pods (200 XP)
│  │  Prerequisites: Level 1
│  │  Skills: Sidecar pattern, container interaction
│  │  
│  ├─ Level 8: Container Logs (150 XP)
│  │  Prerequisites: Level 7
│  │  Skills: Log navigation, debugging multi-container
│  │  
│  ├─ Level 9: Init Containers (150 XP)
│  │  Prerequisites: Level 7
│  │  Skills: Pod lifecycle, init containers
│  │  
│  └─ Level 10: Namespace Quotas (200 XP)
│     Prerequisites: Level 4
│     Skills: Resource management, multi-tenancy
│     
│     🏆 WORLD 1 COMPLETE! You can now debug basic Kubernetes issues!
│
├─ WORLD 2: Deployments & Scaling ⭐⭐
│  │  Difficulty: Intermediate | Time: 4-6 hours | XP: 2,000
│  │  Prerequisites: Complete World 1 (Levels 1-10)
│  │  
│  ├─ Level 11: Deployment Rollback (200 XP)
│  │  Prerequisites: Level 2
│  │  Skills: Rollout management, revision history
│  │  
│  ├─ Level 12: Liveness Probes (200 XP)
│  │  Prerequisites: Level 1, 11
│  │  Skills: Health checks, probe configuration
│  │  
│  ├─ Level 13: Readiness Probes (200 XP)
│  │  Prerequisites: Level 12
│  │  Skills: Traffic management, zero-downtime deploys
│  │  
│  ├─ Level 14: HPA Setup (250 XP)
│  │  Prerequisites: Level 4, 11
│  │  Skills: Autoscaling, metrics-server, resource metrics
│  │  
│  ├─ Level 15: Rollout Strategies (200 XP)
│  │  Prerequisites: Level 11, 13
│  │  Skills: RollingUpdate, maxSurge, maxUnavailable
│  │  
│  ├─ Level 16: PodDisruptionBudget (250 XP)
│  │  Prerequisites: Level 11
│  │  Skills: Availability guarantees, disruption management
│  │  
│  ├─ Level 17: Blue-Green Deployment (200 XP)
│  │  Prerequisites: Level 5, 11
│  │  Skills: Advanced deployment patterns, instant rollback
│  │  
│  ├─ Level 18: Canary Deployment (200 XP)
│  │  Prerequisites: Level 17
│  │  Skills: Progressive delivery, traffic splitting
│  │  
│  ├─ Level 19: StatefulSet vs Deployment (200 XP)
│  │  Prerequisites: Level 11
│  │  Skills: Stateful workloads, persistent storage
│  │  
│  └─ Level 20: ReplicaSet Management (150 XP)
│     Prerequisites: Level 11
│     Skills: Workload controllers, abstraction layers
│     
│     🏆 WORLD 2 COMPLETE! You can now manage production deployments!
│
├─ WORLD 3: Networking & Services ⭐⭐
│  │  Difficulty: Intermediate | Time: 4-6 hours | XP: ~2,000
│  │  Prerequisites: Complete World 2 (Levels 1-20)
│  │  Coming Soon!
│  │  
│  └─ Planned Topics:
│     • Service types (ClusterIP, NodePort, LoadBalancer)
│     • Ingress controllers
│     • Network policies
│     • DNS debugging
│     • Service mesh basics
│
├─ WORLD 4: Storage & StatefulSets ⭐⭐⭐
│  │  Difficulty: Advanced | Time: 5-7 hours | XP: ~2,500
│  │  Prerequisites: Complete World 3
│  │  Coming Soon!
│  │  
│  └─ Planned Topics:
│     • PersistentVolumes and claims
│     • Storage classes
│     • StatefulSet deep dive
│     • Volume snapshots
│     • Data migration
│
└─ WORLD 5: Security & RBAC ⭐⭐⭐
   │  Difficulty: Advanced | Time: 5-7 hours | XP: ~2,500
   │  Prerequisites: Complete World 4
   │  Coming Soon!
   │  
   └─ Planned Topics:
      • RBAC troubleshooting
      • Service accounts
      • Pod security policies
      • Network policies
      • Secret management
```

---

## 🎯 Recommended Learning Paths

### Path A: Absolute Beginner (Never used Kubernetes)
```
Week 1: World 1 - Levels 1-5
  • Focus on core concepts
  • Read all debriefs thoroughly
  • Practice each level until comfortable
  
Week 2: World 1 - Levels 6-10
  • Build on basics
  • Start connecting concepts
  • Complete World 1 certificate
  
Week 3: World 2 - Levels 11-15
  • Deployment fundamentals
  • Take time with probes and HPA
  
Week 4: World 2 - Levels 16-20
  • Advanced patterns
  • Complete World 2 certificate
  
Result: In 1 month, you'll have solid Kubernetes debugging skills
```

### Path B: Some Kubernetes Experience (Used kubectl before)
```
Week 1: World 1 (full) - Speed run
  • Challenge yourself to complete without hints
  • Focus on debriefs for deep learning
  
Week 2: World 2 (full)
  • Deployment patterns will be new territory
  • Take time with HPA and PDB levels
  
Result: In 2 weeks, you'll be production-ready
```

### Path C: Experienced Engineer (Study for CKA/CKAD)
```
Week 1: All levels, exam mode
  • No hints, no guides
  • Time yourself
  • Focus on speed and accuracy
  
Week 2: Review missed concepts
  • Read debriefs for weak areas
  • Practice real-world scenarios
  
Result: Exam-ready in 2 weeks
```

---

## 📋 Prerequisite Map

### Visual Dependencies

```
Level 1 (CrashLoopBackOff)
  ├─→ Level 2 (Deployments)
  │    └─→ Level 5 (Labels)
  │         ├─→ Level 6 (Ports)
  │         └─→ Level 17 (Blue-Green)
  │              └─→ Level 18 (Canary)
  │
  ├─→ Level 3 (ImagePull)
  │
  ├─→ Level 4 (Pending)
  │    ├─→ Level 10 (Quotas)
  │    └─→ Level 14 (HPA)
  │
  ├─→ Level 7 (Multi-container)
  │    ├─→ Level 8 (Logs)
  │    └─→ Level 9 (Init)
  │
  └─→ Level 11 (Rollback)
       ├─→ Level 12 (Liveness)
       │    └─→ Level 13 (Readiness)
       │         └─→ Level 15 (Rollout Strategy)
       │
       ├─→ Level 14 (HPA)
       ├─→ Level 16 (PDB)
       ├─→ Level 19 (StatefulSet)
       └─→ Level 20 (ReplicaSet)
```

---

## 🎓 Skill Progression

### After World 1: Core Basics ✅
**You can:**
- Debug common pod failures independently
- Navigate kubectl commands confidently
- Understand pod lifecycle and status
- Work with namespaces and quotas
- Read and interpret Kubernetes events

**Job Titles:**
- Junior DevOps Engineer
- Platform Engineer (entry level)
- SRE Intern

### After World 2: Deployments & Scaling ✅
**You can:**
- Manage production deployments
- Configure autoscaling
- Implement zero-downtime deployments
- Choose appropriate deployment strategies
- Handle rollback scenarios confidently

**Job Titles:**
- DevOps Engineer
- Platform Engineer
- SRE Engineer
- Kubernetes Administrator

### After World 3: Networking (Coming)
**You will be able to:**
- Debug service discovery issues
- Configure ingress controllers
- Implement network policies
- Troubleshoot DNS problems

### After World 4: Storage (Coming)
**You will be able to:**
- Manage stateful applications
- Configure persistent storage
- Handle data migrations
- Debug volume mount issues

### After World 5: Security (Coming)
**You will be able to:**
- Implement RBAC policies
- Secure cluster access
- Manage secrets safely
- Pass security audits

---

## 📊 Time Estimates by Experience Level

| World | Beginner | Intermediate | Advanced |
|-------|----------|--------------|----------|
| World 1 | 5-8 hours | 3-5 hours | 2-3 hours |
| World 2 | 6-10 hours | 4-6 hours | 3-4 hours |
| Total (1-2) | 11-18 hours | 7-11 hours | 5-7 hours |

**Beginner:** Never used Kubernetes  
**Intermediate:** Have deployed apps to K8s before  
**Advanced:** Use K8s daily, studying for certification  

---

## 🎯 Certification Alignment

### CKAD (Certified Kubernetes Application Developer)
**K8sQuest Coverage:**
- ✅ Core Concepts (World 1)
- ✅ Multi-Container Pods (Level 7-9)
- ✅ Pod Design (World 2)
- ⏳ Services & Networking (World 3)
- ⏳ State Persistence (World 4)

**Recommendation:** Complete Worlds 1-4 for full CKAD readiness

### CKA (Certified Kubernetes Administrator)
**K8sQuest Coverage:**
- ✅ Workloads & Scheduling (Worlds 1-2)
- ⏳ Services & Networking (World 3)
- ⏳ Storage (World 4)
- ⏳ Security (World 5)
- ⏳ Cluster Maintenance (World 6 planned)

**Recommendation:** Complete all worlds + official CKA labs

---

## 💡 Tips for Maximum Learning

### 1. Don't Rush
Each level is designed to teach specific concepts. Spend time understanding WHY, not just HOW.

### 2. Read ALL Debriefs
The debrief.md files contain production incident stories and deep explanations. This is where real learning happens.

### 3. Practice Without Hints First
Try to solve each level yourself before using hints. Struggle = learning.

### 4. Keep the Quick Reference Handy
Print out the QUICK-REFERENCE.md for each world. It's designed as a real-world cheat sheet.

### 5. Build a Personal Playbook
Document your own notes, commands, and patterns as you learn.

### 6. Teach Someone Else
After completing a world, explain the concepts to a colleague. Teaching solidifies learning.

---

## 🏆 Achievement Milestones

- 🥉 **Bronze Explorer** - Complete World 1 (1,450 XP)
- 🥈 **Silver Operator** - Complete World 2 (3,450 total XP)
- 🥇 **Gold Engineer** - Complete World 3 (5,450+ total XP)
- 💎 **Platinum Architect** - Complete World 4 (7,950+ total XP)
- 👑 **K8s Master** - Complete All Worlds (10,000+ total XP)

---

## 🚀 Ready to Start?

```bash
# Begin your journey
./play.sh

# Start with Level 1: CrashLoopBackOff
# No prerequisites needed - just dive in!
```

---

## 📚 Additional Resources

### Before Starting K8sQuest
- [Kubernetes Basics Tutorial](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- [What is a Pod?](https://kubernetes.io/docs/concepts/workloads/pods/)

### While Playing
- Keep kubectl cheat sheet open
- Read official docs when confused
- Join Kubernetes Slack for questions

### After Completing
- Practice on real clusters
- Contribute to open source K8s projects
- Share your learnings with the community

---

**Remember:** K8sQuest is designed for learning by fixing. Every broken resource is an opportunity to understand Kubernetes more deeply!

🎮 **Happy Learning!** 🎮
