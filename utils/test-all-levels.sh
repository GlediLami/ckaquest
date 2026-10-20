#!/bin/bash
# Test script for all K8sQuest levels (1-20)
# Validates that all required files exist and are properly configured

set -e

TOTAL_LEVELS=20
PASSED=0
FAILED=0

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================================="
echo "  K8sQuest Levels 1-20 Validation Test"
echo "=================================================="
echo ""

# Function to test a level
test_level() {
    local level_num=$1
    local level_dir=$2
    local level_name=$3
    
    echo -n "Testing Level $level_num ($level_name)... "
    
    # Check if directory exists
    if [ ! -d "$level_dir" ]; then
        echo -e "${RED}FAIL${NC} - Directory not found"
        ((FAILED++))
        return 1
    fi
    
    # Check required files
    local required_files=(
        "mission.yaml"
        "broken.yaml"
        "validate.sh"
        "hint-1.txt"
        "hint-2.txt"
        "hint-3.txt"
        "debrief.md"
    )
    
    local missing_files=()
    for file in "${required_files[@]}"; do
        if [ ! -f "$level_dir/$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    # Check if validate.sh is executable
    if [ -f "$level_dir/validate.sh" ] && [ ! -x "$level_dir/validate.sh" ]; then
        missing_files+=("validate.sh (not executable)")
    fi
    
    # Check mission.yaml has required fields
    if [ -f "$level_dir/mission.yaml" ]; then
        if ! grep -q "^name:" "$level_dir/mission.yaml" || \
           ! grep -q "^xp:" "$level_dir/mission.yaml" || \
           ! grep -q "^difficulty:" "$level_dir/mission.yaml"; then
            missing_files+=("mission.yaml (missing required fields)")
        fi
    fi
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        echo -e "${GREEN}PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        echo "   Missing/Invalid: ${missing_files[*]}"
        ((FAILED++))
        return 1
    fi
}

# Test World 1: Basics (Levels 1-10)
echo -e "${YELLOW}World 1: Basics (Levels 1-10)${NC}"
echo "--------------------------------------"
test_level 1 "worlds/world-1-basics/level-1-pods" "CrashLoopBackOff"
test_level 2 "worlds/world-1-basics/level-2-deployments" "Deployment Rollback"
test_level 3 "worlds/world-1-basics/level-3-imagepull" "ImagePullBackOff"
test_level 4 "worlds/world-1-basics/level-4-pending" "Pending Pod"
test_level 5 "worlds/world-1-basics/level-5-labels" "Label Selector"
test_level 6 "worlds/world-1-basics/level-6-ports" "Wrong Port"
test_level 7 "worlds/world-1-basics/level-7-multicontainer" "Multi-Container"
test_level 8 "worlds/world-1-basics/level-8-logs" "Missing Logs"
test_level 9 "worlds/world-1-basics/level-9-initcontainer" "Init Container"
test_level 10 "worlds/world-1-basics/level-10-namespace" "Namespace Quota"
echo ""

# Test World 2: Deployments & Scaling (Levels 11-20)
echo -e "${YELLOW}World 2: Deployments & Scaling (Levels 11-20)${NC}"
echo "--------------------------------------"
test_level 11 "worlds/world-2-deployments/level-11-rollback" "The Rollback"
test_level 12 "worlds/world-2-deployments/level-12-liveness" "The Restart Loop"
test_level 13 "worlds/world-2-deployments/level-13-readiness" "Traffic to Unready Pods"
test_level 14 "worlds/world-2-deployments/level-14-hpa" "HPA Can't Scale"
test_level 15 "worlds/world-2-deployments/level-15-rollout" "Zero-Downtime Failure"
test_level 16 "worlds/world-2-deployments/level-16-pdb" "PDB Blocks Evictions"
test_level 17 "worlds/world-2-deployments/level-17-bluegreen" "Blue-Green Gone Wrong"
test_level 18 "worlds/world-2-deployments/level-18-canary" "Canary Imbalance"
test_level 19 "worlds/world-2-deployments/level-19-statefulset" "Stateful App Data Loss"
test_level 20 "worlds/world-2-deployments/level-20-replicaset" "ReplicaSet Chaos"
echo ""

# Summary
echo "=================================================="
echo "  Test Summary"
echo "=================================================="
echo -e "Total Levels Tested: $TOTAL_LEVELS"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All levels validated successfully!${NC}"
    echo "All 20 levels are ready to play."
    exit 0
else
    echo -e "${RED}❌ Some levels have issues.${NC}"
    echo "Please review the failures above."
    exit 1
fi
