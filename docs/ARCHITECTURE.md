# CKAQuest Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        CKAQuest Platform                         │
│                 Kubernetes Training Game System                  │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │         User Interaction Layer            │
        │  • ./play.sh (Game Launcher)              │
        │  • Rich TUI (Colorful Terminal Interface) │
        │  • Interactive Menus & Commands           │
        └───────────────────────────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────┐
        │         Game Engine (engine.py)           │
        │  • Mission Management                     │
        │  • Progressive Hint System (3 tiers)      │
        │  • XP Tracking & Persistence              │
        │  • Real-time Resource Monitoring          │
        │  • Command Validation                     │
        └───────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
        ┌───────────────────┐   ┌───────────────────┐
        │  Safety Module    │   │  Mission Content  │
        │  (safety.py)      │   │  (Worlds 1-5)     │
        │                   │   │                   │
        │  • Pattern Match  │   │  • 50 Levels      │
        │  • RBAC Check     │   │  • Broken Configs │
        │  • Confirmation   │   │  • Solutions      │
        └───────────────────┘   │  • Hints          │
                                │  • Debriefs       │
                                └───────────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────┐
                        │  Kubernetes Cluster       │
                        │  (kind - Local)           │
                        │                           │
                        │  • ckaquest namespace     │
                        │  • RBAC Isolation         │
                        │  • Safe Playground        │
                        └───────────────────────────┘

═══════════════════════════════════════════════════════════════════

                        Data Flow Diagram

    User Input              Game Engine              Kubernetes
        │                       │                        │
        │  Play Level          │                        │
        │─────────────────────>│                        │
        │                       │  Apply broken.yaml    │
        │                       │───────────────────────>│
        │                       │                        │
        │  Request Hint        │                        │
        │─────────────────────>│                        │
        │<─────────────────────│                        │
        │   Display Hint 1     │                        │
        │                       │                        │
        │  kubectl commands    │                        │
        │──────────────────────────────────────────────>│
        │                       │  Safety Check         │
        │<──────────────────────│                        │
        │   Confirm/Block      │                        │
        │                       │                        │
        │  Validate Solution   │                        │
        │─────────────────────>│                        │
        │                       │  Run validate.sh      │
        │                       │───────────────────────>│
        │                       │<───────────────────────│
        │                       │   Pass/Fail           │
        │<─────────────────────│                        │
        │   Show Debrief       │                        │
        │   Award XP           │                        │

═══════════════════════════════════════════════════════════════════

                    Level Structure (Template)

worlds/
└── world-X-name/
    └── level-Y-topic/
        ├── mission.yaml          ← Metadata (name, XP, difficulty, concepts)
        ├── broken.yaml          ← Intentionally broken K8s resources
        ├── solution.yaml        ← (Optional) Fixed version
        ├── validate.sh          ← Pass/fail test script
        ├── hint-1.txt           ← Observation hint
        ├── hint-2.txt           ← Direction hint
        ├── hint-3.txt           ← Near-solution hint
        └── debrief.md           ← Post-mission learning
                                   • What happened
                                   • How K8s behaved
                                   • Mental model
                                   • Real-world incident
                                   • Commands learned

═══════════════════════════════════════════════════════════════════

                    Safety System Architecture

┌──────────────────────────────────────────────────────────────────┐
│                     Safety Guard Layers                          │
└──────────────────────────────────────────────────────────────────┘

Layer 1: Command Pattern Validation (safety.py)
┌────────────────────────────────────────────────────────────┐
│  • Regex pattern matching                                  │
│  • Dangerous commands: delete namespace, --all flags, etc. │
│  • Severity levels: CRITICAL (block) | WARNING (confirm)   │
│  • Rich UI for user feedback                              │
└────────────────────────────────────────────────────────────┘
                            ↓ (if allowed)
Layer 2: RBAC Enforcement (Kubernetes)
┌────────────────────────────────────────────────────────────┐
│  • ServiceAccount: ckaquest-player                         │
│  • Namespace: ckaquest (isolated)                          │
│  • Role: Full access ONLY in ckaquest namespace            │
│  • ClusterRole: Read-only cluster-wide                     │
└────────────────────────────────────────────────────────────┘
                            ↓
Layer 3: Namespace Isolation (Kubernetes)
┌────────────────────────────────────────────────────────────┐
│  • All operations scoped to 'ckaquest' namespace           │
│  • System namespaces protected (kube-system, default)      │
│  • Resource quotas can limit usage                         │
└────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

                    World Progression Path

┌─────────────────────────────────────────────────────────────┐
│  WORLD 1: Core Kubernetes Basics (Levels 1-10) 🚧          │
│  Difficulty: ⭐ Beginner                                    │
│  XP: 1,450                                                  │
│  Status: COMPLETE                                           │
│                                                             │
│  Topics: Pods, Deployments, Labels, Ports, Logs,          │
│          Namespaces, Init Containers                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  WORLD 2: Deployments & Scaling (Levels 11-20) 🚧          │
│  Difficulty: ⭐⭐ Intermediate                              │
│  XP: 2,000                                                  │
│  Status: BLUEPRINTED                                        │
│                                                             │
│  Topics: Rolling Updates, HPA, Probes, Rollbacks,          │
│          Blue-Green, Canary, PDB, StatefulSets             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  WORLD 3: Networking & Services (Levels 21-30) 🚧          │
│  Difficulty: ⭐⭐ Intermediate                              │
│  XP: 2,300                                                  │
│  Status: BLUEPRINTED                                        │
│                                                             │
│  Topics: Services, Ingress, DNS, NetworkPolicy,            │
│          Session Affinity, Cross-namespace                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  WORLD 4: Storage & Stateful Apps (Levels 31-40) 🚧        │
│  Difficulty: ⭐⭐⭐ Advanced                                │
│  XP: 2,600                                                  │
│  Status: BLUEPRINTED                                        │
│                                                             │
│  Topics: PV/PVC, StatefulSets, StorageClass, ConfigMaps,   │
│          Secrets, Volume Permissions                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  WORLD 5: Security & Production Ops (Levels 41-50) 🚧      │
│  Difficulty: ⭐⭐⭐ Advanced                                │
│  XP: 3,150                                                  │
│  Status: BLUEPRINTED                                        │
│                                                             │
│  Topics: RBAC, SecurityContext, ResourceQuotas,            │
│          LimitRanges, PSP, Node Affinity, Taints,          │
│          🔥 CHAOS FINALE (Level 50)                        │
└─────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

                    Technology Stack

┌─────────────────────┬─────────────────────────────────────────┐
│ Component           │ Technology                              │
├─────────────────────┼─────────────────────────────────────────┤
│ Game Engine         │ Python 3.x                              │
│ UI Framework        │ rich (Python TUI library)               │
│ Kubernetes          │ kind (Kubernetes in Docker)             │
│ Container Runtime   │ Docker Desktop                          │
│ CLI Tool            │ kubectl                                 │
│ Data Format         │ YAML (configs), JSON (progress)         │
│ Scripting           │ Bash (automation, validation)           │
│ Testing             │ Python unittest-style (pytest patterns) │
│ Version Control     │ Git (.gitignore configured)             │
│ Isolation           │ Python venv (dependency management)     │
└─────────────────────┴─────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

                    Key Metrics Dashboard

┌────────────────────────────────────────────────────────────────┐
│  📊 CKAQuest Statistics                                        │
├────────────────────────────────────────────────────────────────┤
│  Total Levels:              50 (10 complete, 40 blueprinted)  │
│  Total XP Available:        11,500                            │
│  Worlds:                    5                                 │
│  Lines of Code (Engine):    ~1,500                            │
│  Lines of Documentation:    ~3,000+                           │
│  Safety Test Coverage:      20 tests, 100% passing            │
│  Setup Time:                ~5 minutes                        │
│  Avg Level Duration:        10-15 minutes                     │
│  Learning Outcomes:         CKA exam preparation level        │
└────────────────────────────────────────────────────────────────┘

Created with ❤️ for Kubernetes learners worldwide
```