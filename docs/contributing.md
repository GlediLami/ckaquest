# Contributing to CKAQuest

## 🎯 Mission: Create Consistent, High-Quality Challenges

Welcome, contributor! This guide will help you create new CKAQuest challenges that are maintainable, consistent, and provide actual learning value.

**CKAQuest is now COMPLETE with all 50 levels across 5 worlds!** However, we welcome:
- Bug fixes and improvements to existing levels
- New bonus levels or alternative challenges
- Translations and localization
- Documentation improvements
- Engine enhancements

## 📁 Required File Structure (8 Files Per Level)

Every challenge MUST have this structure:

```
worlds/
  world-X-name/
    level-Y-name/
      ├── mission.yaml      # REQUIRED: Challenge metadata
      ├── broken.yaml       # REQUIRED: The broken K8s resources
      ├── solution.yaml     # REQUIRED: The fixed configuration
      ├── validate.sh       # REQUIRED: Pass/fail test script (must be executable)
      ├── hint-1.txt        # REQUIRED: Initial observation hint
      ├── hint-2.txt        # REQUIRED: Direction hint
      ├── hint-3.txt        # REQUIRED: Near-solution hint
      └── debrief.md        # REQUIRED: Post-completion learning guide
```

**All 8 files are mandatory.** This ensures consistency across all 50 levels.

## 📋 File Requirements

### 1. mission.yaml

Metadata describing the challenge.

```yaml
level: 42
title: "SecurityContext Privilege Escalation"
description: "The web-app pod is failing security admission. Fix the SecurityContext to run as non-root."
difficulty: intermediate
xp_reward: 250
world: 5
estimated_time: "10-15 minutes"
concepts:
  - securitycontext
  - pod-security
  - non-root
learning_objectives:
  - Understand SecurityContext configuration
  - Configure runAsNonRoot and allowPrivilegeEscalation
  - Meet Pod Security Standards requirements
```

**Rules:**
- `level`: Sequential number (1-50)
- `title`: Max 60 characters, clear and descriptive
- `xp_reward`: 100 (beginner), 150-250 (intermediate), 300-350 (advanced), 500 (expert finale)
- `difficulty`: beginner | intermediate | advanced | expert
- `estimated_time`: Realistic for target skill level
- `concepts`: 2-5 concepts, lowercase, hyphenated
- `learning_objectives`: 3-5 specific learning outcomes

### 2. broken.yaml

The intentionally broken Kubernetes resources that students must fix.

**Rules:**
- Must be valid YAML syntax
- Must deploy without syntax errors (broken behavior ≠ malformed YAML)
- Should demonstrate ONE specific misconfiguration
- Must use namespace `ckaquest` for all namespaced resources
- Include comments explaining what's wrong (for educational value)
- Use realistic resource names and configurations

**Example:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-app
  namespace: ckaquest
spec:
  containers:
  - name: web
    image: nginx:latest
    securityContext:
      runAsUser: 0  # ❌ Running as root - violates security policy
      allowPrivilegeEscalation: true  # ❌ Allows privilege escalation
```

### 3. solution.yaml

The corrected configuration that fixes the issue.

**Rules:**
- Must pass validation script
- Include comments explaining the fix
- Should represent best practices
- Must be a complete, working configuration

**Example:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-app
  namespace: ckaquest
spec:
  securityContext:
    runAsNonRoot: true  # ✅ Require non-root user
    runAsUser: 1000     # ✅ Run as specific non-root user
    fsGroup: 2000
  containers:
  - name: web
    image: nginx:latest
    securityContext:
      allowPrivilegeEscalation: false  # ✅ Prevent privilege escalation
      capabilities:
        drop:
        - ALL  # ✅ Drop all capabilities
```

### 4. validate.sh

Bash script that returns 0 (success) or 1 (failure). Must be executable.

**Template for simple validation:**
```bash
#!/bin/bash

NAMESPACE="ckaquest"
POD_NAME="web-app"

echo "🔍 Validating SecurityContext configuration..."

# Check if pod exists
if ! kubectl get pod $POD_NAME -n $NAMESPACE &>/dev/null; then
    echo "❌ Pod not found"
    exit 1
fi

# Check runAsNonRoot
RUN_AS_NON_ROOT=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.containers[0].securityContext.runAsNonRoot}')
if [ "$RUN_AS_NON_ROOT" != "true" ]; then
    echo "❌ runAsNonRoot not set to true"
    exit 1
fi

# Check allowPrivilegeEscalation
ALLOW_PRIV=$(kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath='{.spec.containers[0].securityContext.allowPrivilegeEscalation}')
if [ "$ALLOW_PRIV" != "false" ]; then
    echo "❌ allowPrivilegeEscalation not set to false"
    exit 1
fi

echo "✅ SUCCESS! SecurityContext properly configured!"
exit 0
```

**Template for multi-stage validation:**
```bash
#!/bin/bash

NAMESPACE="ckaquest"
ERRORS=0

echo "🔍 MULTI-STAGE VALIDATION"
echo ""

# Stage 1
echo "Stage 1: Checking pod exists..."
if ! kubectl get pod web-app -n $NAMESPACE &>/dev/null; then
    echo "❌ FAILED: Pod not found"
    ((ERRORS++))
else
    echo "✅ PASSED"
fi

# Stage 2
echo "Stage 2: Checking SecurityContext..."
# ... validation logic ...

# Final result
if [ $ERRORS -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED!"
    exit 0
else
    echo "❌ $ERRORS check(s) failed"
    exit 1
fi
```

**Important:**
- Make executable: `chmod +x validate.sh`
- Use clear stage-by-stage output
- Provide helpful error messages
- Exit 0 for success, 1 for failure

### 5. debrief.md (MOST IMPORTANT!)

Post-completion learning guide - this is where real learning happens!

**Required Sections:**

1. **What You Just Fixed** - Clear explanation of the problem
2. **Why It Was Broken** - Root cause analysis
3. **The Solution** - Step-by-step breakdown of the fix
4. **Key Concepts** - Deep dive into the concepts
5. **Real-World Scenario** - Production incident example with costs/impact
6. **Best Practices** - Production recommendations
7. **Common Pitfalls** - What to avoid
8. **Verification Commands** - How to check your work
9. **Further Reading** - Official docs and resources

**Example Structure:**
```markdown
# Level 42 Debrief: SecurityContext Privilege Escalation

## What You Just Fixed

The web-app pod was being rejected by the Pod Security admission controller because it was configured to run as root with privilege escalation enabled.

## Why It Was Broken

The SecurityContext had:
- `runAsUser: 0` (root user)
- `allowPrivilegeEscalation: true`
- No capability restrictions

This violates the "restricted" Pod Security Standard.

## The Solution

Applied proper SecurityContext:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  capabilities:
    drop: [ALL]
```

## Key Concepts

### SecurityContext
Controls security settings for pods and containers...

## Real-World Scenario

**Incident**: Container escape in production (March 2023)
**Impact**: $5.4M in cryptomining charges
**Cause**: Pod running as root with privilege escalation
**Resolution**: Enforced restricted Pod Security Standard

[Continue with full debrief...]
```

**Aim for 2,000-5,000 words of comprehensive educational content.**

### 6-8. hint-{1,2,3}.txt

Progressive hints that unlock gradually. Each should build on the previous.

**hint-1.txt** - Initial observations and investigation commands:
```
💡 Hint 1: Initial Investigation

The pod is failing to start. Let's investigate:

1. Check pod status:
   kubectl get pod web-app -n ckaquest
   
2. Look for events:
   kubectl describe pod web-app -n ckaquest
   
3. Check for security-related errors in events

Look for admission controller rejection messages!
```

**hint-2.txt** - Point toward the solution area:
```
💡 Hint 2: Security Context

The pod is being rejected by the Pod Security admission controller.

The issue is in the SecurityContext configuration:
- Check runAsUser value
- Check allowPrivilegeEscalation setting
- Check capability restrictions

What values would meet the "restricted" security standard?
```

**hint-3.txt** - Near-complete solution:
```
💡 Hint 3: The Fix

You need to configure SecurityContext to:

1. Run as non-root:
   runAsNonRoot: true
   runAsUser: 1000

2. Prevent privilege escalation:
   allowPrivilegeEscalation: false

3. Drop all capabilities:
   capabilities:
     drop: [ALL]

Apply these in both pod-level and container-level securityContext!
```

**Progression:**
- Hint 1: "Where to look"
- Hint 2: "What to focus on"
- Hint 3: "How to fix it"

## 🚫 What NOT to Do

❌ **Don't create multi-issue challenges** (except for special finale levels)
- Each level should teach ONE concept clearly
- Multiple issues confuse learners

❌ **Don't require external tools** (helm, kustomize, operators, etc.)
- Keep it kubectl-only for consistency
- External tools add complexity

❌ **Don't use real secrets/credentials**
- Use obviously fake values: `password123`, `fake-token`
- Never commit real credentials

❌ **Don't break multiple namespaces**
- All resources in `ckaquest` namespace only
- Don't affect system namespaces

❌ **Don't make it a guessing game**
- Provide clear error messages
- Validation should guide users
- Hints should actually help

❌ **Don't skip the debrief**
- This is the most important learning moment
- Include real-world examples and incidents
- Explain the "why" not just the "how"

❌ **Don't forget to test**
- Test on a fresh cluster
- Verify both broken and fixed states
- Check all 8 files are present

## ✅ Quality Checklist

Before submitting a new level, verify:

### Files
- [ ] All 8 required files present (mission.yaml, broken.yaml, solution.yaml, validate.sh, hint-1/2/3.txt, debrief.md)
- [ ] validate.sh is executable (`chmod +x validate.sh`)
- [ ] No extra or missing files

### Content Quality
- [ ] mission.yaml has all required fields
- [ ] broken.yaml uses valid YAML syntax
- [ ] broken.yaml demonstrates clear, single issue
- [ ] solution.yaml fixes the issue completely
- [ ] validate.sh passes with solution.yaml
- [ ] validate.sh fails with broken.yaml
- [ ] Hints progress logically (investigate → identify → fix)
- [ ] debrief.md has all required sections
- [ ] debrief.md includes real-world incident example
- [ ] debrief.md is 2,000-5,000 words

### Testing
- [ ] Tested on fresh kind cluster
- [ ] Applied broken.yaml - verifies it's broken
- [ ] Applied solution.yaml - verifies it works
- [ ] Ran validate.sh with both states
- [ ] Checked for helpful error messages
- [ ] Verified namespace isolation (ckaquest only)

### Best Practices
- [ ] Single, clear learning objective
- [ ] Comments in YAML explaining issues
- [ ] Clear, beginner-friendly language
- [ ] Consistent with existing level patterns
- [ ] No external tool dependencies
- [ ] Appropriate difficulty and XP reward

## 🧪 Testing Your Challenge

### Step 1: Setup Fresh Environment
```bash
# Make sure you have a clean cluster
kind delete cluster --name ckaquest
kind create cluster --name ckaquest

# Create ckaquest namespace
kubectl create namespace ckaquest
```

### Step 2: Test Broken State
```bash
# Apply the broken configuration
kubectl apply -f worlds/world-X-name/level-Y-name/broken.yaml

# Verify it's actually broken
./worlds/world-X-name/level-Y-name/validate.sh
# Should exit with code 1 and show helpful error
```

### Step 3: Test Solution
```bash
# Apply the solution
kubectl apply -f worlds/world-X-name/level-Y-name/solution.yaml

# Verify it passes validation
./worlds/world-X-name/level-Y-name/validate.sh
# Should exit with code 0 and show success message
```

### Step 4: Test Hints
```bash
# Read through each hint
cat hint-1.txt
cat hint-2.txt
cat hint-3.txt

# Verify they progress logically
# Verify hint-3 leads clearly to solution
```

### Step 5: Review Debrief
```bash
# Check debrief content
cat debrief.md

# Verify:
# - All required sections present
# - Real-world incident included
# - Best practices documented
# - 2,000+ words of content
```

## 📚 Reference Examples

### Beginner Level Examples
- `worlds/world-1-basics/level-1-pods/` - CrashLoopBackOff
- `worlds/world-1-basics/level-2-deployments/` - Zero Replicas
- `worlds/world-1-basics/level-3-imagepull/` - ImagePullBackOff

### Intermediate Level Examples
- `worlds/world-2-deployments/level-13-readiness/` - Readiness Probes
- `worlds/world-3-networking/level-24-ingress/` - Ingress Configuration
- `worlds/world-4-storage/level-32-volume-mount/` - Volume Mounts

### Advanced Level Examples
- `worlds/world-5-security/level-41-rbac-permission/` - RBAC
- `worlds/world-5-security/level-44-networkpolicy/` - NetworkPolicy
- `worlds/world-5-security/level-48-pod-security/` - Pod Security Standards

### Expert Level Example
- `worlds/world-5-security/level-50-chaos-finale/` - Multi-concept finale

## 🎯 XP Reward Guidelines

Choose XP based on difficulty and learning value:

- **100 XP**: Simple beginner concepts (single field fix)
- **150-200 XP**: Intermediate single-concept (requires understanding)
- **250-300 XP**: Advanced concepts or multi-step fixes
- **350 XP**: Complex advanced concepts
- **500 XP**: Expert finale levels combining multiple concepts

## 🌍 World Structure

Levels are organized into worlds by theme:

- **World 1 (1-10)**: Basics - Pods, Deployments, Labels, Namespaces
- **World 2 (11-20)**: Deployments & Scaling - Updates, HPA, Probes
- **World 3 (21-30)**: Networking - Services, Ingress, DNS, NetworkPolicy
- **World 4 (31-40)**: Storage - PVs, PVCs, StatefulSets, ConfigMaps
- **World 5 (41-50)**: Security & Production - RBAC, Security, Resources

New levels should fit logically into existing worlds or propose a new themed world.

## 🤝 Submission Process

1. **Fork the repository**
2. **Create a new branch**: `git checkout -b level-51-your-feature`
3. **Create all 8 required files**
4. **Test thoroughly** using checklist above
5. **Make validate.sh executable**: `chmod +x validate.sh`
6. **Commit with clear message**: `git commit -m "Add Level 51: Your Feature Name"`
7. **Push to your fork**: `git push origin level-51-your-feature`
8. **Open Pull Request** with:
   - Clear description of the level
   - Why this concept is important
   - What makes it unique from existing levels
   - Screenshots/examples of broken and fixed states

## 💡 Tips for Great Levels

### Make It Real
- Base scenarios on actual production incidents
- Use realistic configurations
- Include cost/impact data in debriefs

### Keep It Focused
- One concept per level (except finales)
- Clear learning objective
- Direct path from broken → fixed

### Be Educational
- Explain the "why" not just "what"
- Include mental models in debriefs
- Show how to verify the fix
- Link to official documentation

### Test Everything
- Fresh cluster validation
- Both broken and fixed states
- All hints and validation messages
- Complete playthrough as a learner

## 📞 Questions?

- Check existing levels for patterns
- Review [ARCHITECTURE.md](ARCHITECTURE.md)
- Open an issue for discussion
- Join community discussions

**Thank you for contributing to CKAQuest!** 🚀
