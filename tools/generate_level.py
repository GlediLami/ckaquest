#!/usr/bin/env python3
"""
K8sQuest Level Generator
Creates a complete level structure from a template
"""

import sys
import yaml
from pathlib import Path

def create_level(world, level_num, level_name, config):
    """Create a complete level structure"""
    
    # Create level directory
    level_dir = Path(f"worlds/{world}/level-{level_num}-{level_name}")
    level_dir.mkdir(parents=True, exist_ok=True)
    
    # Create mission.yaml
    mission = {
        "name": config["name"],
        "description": config["description"],
        "objective": config["objective"],
        "xp": config.get("xp", 100),
        "difficulty": config.get("difficulty", "beginner"),
        "expected_time": config.get("expected_time", "10m"),
        "concepts": config.get("concepts", [])
    }
    
    with open(level_dir / "mission.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(mission, f, default_flow_style=False)
    
    # Create broken.yaml
    with open(level_dir / "broken.yaml", 'w', encoding='utf-8') as f:
        f.write(config.get("broken_yaml", "# Add broken resources here\n"))
    
    # Create validate.sh
    validate_script = config.get("validate_script", """#!/bin/bash
# Add validation logic here
echo "✅ Validation passed"
exit 0
""")
    
    with open(level_dir / "validate.sh", 'w', encoding='utf-8') as f:
        f.write(validate_script)
    
    # Make validate.sh executable
    (level_dir / "validate.sh").chmod(0o755)
    
    # Create hints
    hints = config.get("hints", [
        "Check the resource status",
        "Look at the events and logs",
        "Fix the issue and validate"
    ])
    
    for i, hint in enumerate(hints[:3], 1):
        with open(level_dir / f"hint-{i}.txt", 'w', encoding='utf-8') as f:
            f.write(hint)
    
    # Create debrief.md
    debrief = config.get("debrief", f"""# 🎓 Mission Debrief: {config['name']}

## What Happened

{config['description']}

## How Kubernetes Behaved

[Explain K8s behavior here]

## The Correct Mental Model

[Explain concepts here]

## Real-World Incident Example

[Add production story here]

## Commands You Mastered

[List kubectl commands here]
""")
    
    with open(level_dir / "debrief.md", 'w', encoding='utf-8') as f:
        f.write(debrief)
    
    # Create solution.yaml if provided
    if "solution_yaml" in config:
        with open(level_dir / "solution.yaml", 'w', encoding='utf-8') as f:
            f.write(config["solution_yaml"])
    
    print(f"✅ Created: {level_dir}")
    return level_dir

if __name__ == "__main__":
    print("K8sQuest Level Generator")
    print("This tool helps create level structures quickly")
    print("Edit this script to add level configurations")
