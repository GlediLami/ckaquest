# 🎓 LEVEL 47 DEBRIEF: PodDisruptionBudget

**Congratulations!** You've mastered PodDisruptionBudgets - maintaining availability during disruptions!

---

## 📊 What You Fixed

**Problem:** PDB requires 3 pods, deployment has 2
```yaml
replicas: 2
minAvailable: 3  # Impossible!
```

**Solution:** Scaled deployment and adjusted PDB
```yaml
replicas: 3
minAvailable: 2  # ✅ Can lose 1 pod
```

---

## 🎯 Understanding PodDisruptionBudget

### Purpose
Maintain availability during **voluntary disruptions**:
- Node drains
- Deployments updates  
- Cluster upgrades

### Two Settings

**minAvailable** (how many must stay up):
```yaml
spec:
  minAvailable: 2  # Keep 2 running
```

**maxUnavailable** (how many can be down):
```yaml
spec:
  maxUnavailable: 1  # Max 1 down
```

Use one or the other, not both!

---

## 🔧 Common Patterns

### High Availability
```yaml
# Keep 80% available
spec:
  minAvailable: 80%
```

### Allow Rolling Updates
```yaml
# Can update 1 at a time
spec:
  maxUnavailable: 1
```

### Critical Services
```yaml
# Keep all but one
spec:
  minAvailable: "N-1"  # If you have N replicas
```

---

## 💥 Common Mistakes

1. **minAvailable > replicas**: Impossible to satisfy
2. **Both min and max**: Use one only
3. **PDB without selector**: Won't match pods
4. **Forgetting to scale**: PDB blocks if not enough pods

---

## 🎯 Key Takeaways

1. **PDB = availability during disruptions**
2. **minAvailable** or **maxUnavailable** (not both)
3. **Must be satisfiable**: min ≤ replicas
4. **Voluntary only**: Doesn't prevent node failures
5. **Balance**: Availability vs maintenance flexibility

---

## 🚀 Next Steps

- **Level 48:** Pod Security Standards
- **Level 49:** PriorityClass  
- **Level 50:** CHAOS FINALE!

**Great work!** 🎉🛡️
